import os
from typing import List, Dict, Any, Optional
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import ollama
from .models import RuleMatch

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_local_model = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.local_model = None
        self.local_tokenizer = None
        
        if self.use_local_model:
            self._initialize_local_model()

    def _initialize_local_model(self):
        """Initialize local LLM model (either Ollama or HuggingFace)"""
        try:
            # Try Ollama first
            try:
                ollama.pull(self.ollama_model)
                logger.info(f"Ollama model {self.ollama_model} loaded successfully")
                return
            except Exception as e:
                logger.warning(f"Failed to load Ollama model: {str(e)}")
                logger.info("Falling back to HuggingFace model")

            # Fallback to HuggingFace model
            model_name = "mistralai/Mistral-7B-v0.1"
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            logger.info("HuggingFace model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading local LLM model: {str(e)}")
            raise

    async def generate_explanations(self, rule_matches: List[RuleMatch]) -> List[Dict[str, Any]]:
        """Generate explanations for rule matches using LLM"""
        explanations = []
        
        for match in rule_matches:
            try:
                if self.use_local_model:
                    explanation = await self._generate_local_explanation(match)
                else:
                    explanation = await self._generate_openai_explanation(match)
                
                explanations.append({
                    "rule_id": match.rule_id,
                    "explanation": explanation,
                    "confidence": match.confidence_score,
                    "model": "ollama" if self.use_local_model else "openai"
                })
                
            except Exception as e:
                logger.error(f"Error generating explanation: {str(e)}")
                # Fallback to simple explanation
                explanations.append({
                    "rule_id": match.rule_id,
                    "explanation": match.explanation,
                    "confidence": match.confidence_score,
                    "model": "fallback"
                })
        
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