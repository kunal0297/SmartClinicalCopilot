import os
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import ollama
from datetime import datetime
from .models import RuleMatch
from .metrics.metrics_manager import MetricsManager
from .cache_manager import CacheManager
from .iris_client import IRISClient  # New import for IRIS integration
from .llm_explainer import LLMExplainer  # Add import for LLMExplainer

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_local_model = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.local_model = None
        self.local_tokenizer = None
        self.pipeline = None
        self.metrics_manager = MetricsManager()
        self.cache_manager = CacheManager()
        self.iris_client = IRISClient()  # Initialize IRIS client
        self.llm_explainer = LLMExplainer()  # Initialize LLMExplainer
        self.model_configs = self._load_model_configs()
        
        if self.use_local_model:
            self._initialize_local_model()

    def _load_model_configs(self) -> Dict[str, Any]:
        return {
            "mistral": {
                "max_length": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            },
            "llama2": {
                "max_length": 4096,
                "temperature": 0.8,
                "top_p": 0.95,
                "repetition_penalty": 1.2
            },
            "meditron": {  # Added medical-specific model
                "max_length": 4096,
                "temperature": 0.6,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
        }

    async def _initialize_local_model(self):
        """Initialize local model with better error handling and model selection"""
        try:
            model_name = os.getenv("LOCAL_MODEL_NAME", "mistralai/Mistral-7B-v0.1")
            
            # Load tokenizer first
            self.local_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            # Load model with optimized settings
            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                load_in_8bit=True,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            
            # Initialize pipeline for easier inference
            self.pipeline = pipeline(
                "text-generation",
                model=self.local_model,
                tokenizer=self.local_tokenizer,
                device_map="auto"
            )
            
            logger.info(f"Successfully loaded local model: {model_name}")
            
        except Exception as e:
            logger.error(f"Critical error loading local LLM model: {str(e)}")
            raise

    async def generate_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate a comprehensive patient summary using local LLM and IRIS data"""
        try:
            # Fetch patient data from IRIS
            patient_data = await self.iris_client.get_patient_data(patient_id)
            
            # Create a detailed prompt for the summary
            prompt = self._create_patient_summary_prompt(patient_data)
            
            # Generate summary using local model
            if self.use_local_model:
                summary = await self._generate_local_summary(prompt)
            else:
                summary = await self._generate_openai_summary(prompt)
            
            # Store the summary in IRIS
            await self.iris_client.store_patient_summary(patient_id, summary)
            
            return {
                "patient_id": patient_id,
                "summary": summary,
                "generated_at": datetime.now().isoformat(),
                "model": "local" if self.use_local_model else "openai"
            }
            
        except Exception as e:
            logger.error(f"Error generating patient summary: {str(e)}")
            raise

    def _create_patient_summary_prompt(self, patient_data: Dict[str, Any]) -> str:
        """Create a detailed prompt for patient summary generation"""
        return f"""
        Please provide a comprehensive medical summary for the following patient:

        Patient Information:
        - ID: {patient_data.get('id')}
        - Age: {patient_data.get('age')}
        - Gender: {patient_data.get('gender')}
        
        Medical History:
        {patient_data.get('medical_history', '')}
        
        Current Medications:
        {patient_data.get('medications', '')}
        
        Recent Lab Results:
        {patient_data.get('lab_results', '')}
        
        Recent Diagnoses:
        {patient_data.get('diagnoses', '')}
        
        Please provide a structured summary that includes:
        1. Key medical conditions and their status
        2. Current treatment plan
        3. Recent significant findings
        4. Potential risk factors
        5. Recommended follow-up actions
        
        Summary:
        """

    async def _generate_local_summary(self, prompt: str) -> str:
        """Generate summary using local LLM"""
        try:
            if self.pipeline:
                # Use pipeline for more efficient generation
                outputs = self.pipeline(
                    prompt,
                    max_length=1000,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                return outputs[0]['generated_text']
            else:
                # Fallback to direct model generation
                inputs = self.local_tokenizer(prompt, return_tensors="pt").to(self.local_model.device)
                with torch.no_grad():
                    outputs = self.local_model.generate(
                        **inputs,
                        max_length=1000,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True
                    )
                return self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
        except Exception as e:
            logger.error(f"Error with local LLM summary generation: {str(e)}")
            raise

    async def _generate_openai_summary(self, prompt: str) -> str:
        """Generate summary using OpenAI API"""
        try:
            import openai
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical summarization system. Provide clear, concise, and accurate summaries of patient medical information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            raise

    async def generate_explanations(
        self,
        rule_matches: List[RuleMatch],
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        explanations = []
        
        for match in rule_matches:
            cache_key = f"explanation_{match.rule_id}_{hash(str(match))}"
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                explanations.append(cached_result)
                continue

            for attempt in range(max_retries):
                try:
                    if self.use_local_model:
                        explanation = await self._generate_local_explanation(match)
                    else:
                        explanation = await self._generate_openai_explanation(match)

                    result = {
                        "rule_id": match.rule_id,
                        "explanation": explanation,
                        "confidence": match.confidence_score,
                        "model": "ollama" if self.use_local_model else "openai",
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    await self.cache_manager.set(cache_key, result)
                    await self.metrics_manager.record_llm_metrics(result)
                    
                    explanations.append(result)
                    break
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        explanations.append(self._get_fallback_explanation(match))
        
        return explanations

    async def _generate_openai_explanation(self, match: RuleMatch) -> str:
        """Generate explanation using OpenAI API"""
        try:
            import openai
            
            prompt = self._create_explanation_prompt(match)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a clinical decision support system explaining medical alerts. Provide clear, evidence-based explanations that are easy for healthcare providers to understand."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            raise

    async def _generate_local_explanation(self, match: RuleMatch) -> str:
        """Generate explanation using local LLM (Ollama or HuggingFace)"""
        try:
            prompt = self._create_explanation_prompt(match)
            
            # Try Ollama first
            try:
                response = ollama.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    system="You are a clinical decision support system explaining medical alerts. Provide clear, evidence-based explanations that are easy for healthcare providers to understand.",
                    temperature=0.7,
                    max_tokens=150
                )
                return response['response']
            except Exception as e:
                logger.warning(f"Ollama generation failed: {str(e)}")
                logger.info("Falling back to HuggingFace model")
            
            # Fallback to HuggingFace model
            inputs = self.local_tokenizer(prompt, return_tensors="pt").to(self.local_model.device)
            
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
            
            explanation = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return explanation.split("Explanation:")[-1].strip()
            
        except Exception as e:
            logger.error(f"Error with local LLM: {str(e)}")
            raise

    def _create_explanation_prompt(self, match: RuleMatch) -> str:
        """Create a detailed prompt for explanation generation"""
        return f"""
        Please explain the following clinical alert in a clear and concise way:

        Rule ID: {match.rule_id}
        Alert Type: {match.alert_type}
        Severity: {match.severity}
        Patient Context: {match.patient_context}
        Clinical Data: {match.clinical_data}
        Confidence Score: {match.confidence_score}

        Provide a clear explanation that:
        1. Explains why this alert was triggered
        2. Describes the potential clinical implications
        3. Suggests appropriate next steps
        4. References relevant clinical guidelines if applicable

        Explanation:
        """

    async def generate_shap_explanation(self, rule_match: RuleMatch) -> Dict[str, Any]:
        """Generate SHAP-based explanation for rule match"""
        try:
            # In a real system, this would use actual SHAP values
            # For now, we'll simulate feature importance
            features = self._extract_features(rule_match)
            
            # Simulate SHAP values
            shap_values = {
                feature: self._simulate_shap_value(feature, rule_match)
                for feature in features
            }
            
            return {
                "rule_id": rule_match.rule_id,
                "shap_values": shap_values,
                "base_value": 0.5,  # Simulated base value
                "prediction": rule_match.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            raise

    def _extract_features(self, rule_match: RuleMatch) -> List[str]:
        """Extract features from rule match for SHAP analysis"""
        features = []
        if isinstance(rule_match.details, dict):
            for key, value in rule_match.details.items():
                if isinstance(value, (int, float, str, bool)):
                    features.append(key)
        return features

    def _simulate_shap_value(self, feature: str, rule_match: RuleMatch) -> float:
        """Simulate SHAP value for a feature"""
        # In a real system, this would use actual SHAP calculations
        import random
        return random.uniform(-1, 1)  # Simulated SHAP value