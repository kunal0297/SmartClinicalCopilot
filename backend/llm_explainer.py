import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMExplainer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key found. Explanations will be template-based only.")
        else:
            openai.api_key = self.api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def explain(self, rule_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an explanation for a triggered rule using LLM."""
        try:
            if not self.api_key:
                return self._generate_template_explanation(rule_id, patient_data)

            # Prepare the prompt
            prompt = self._create_prompt(rule_id, patient_data)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a clinical decision support system that provides clear, evidence-based explanations for medical alerts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            explanation = response.choices[0].message.content

            return {
                "rule_id": rule_id,
                "explanation": explanation,
                "confidence": 0.9,
                "references": self._get_references(rule_id)
            }

        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._generate_template_explanation(rule_id, patient_data)

    def _create_prompt(self, rule_id: str, patient_data: Dict[str, Any]) -> str:
        """Create a prompt for the LLM based on the rule and patient data."""
        return f"""
        Generate a clear, evidence-based explanation for why this clinical alert was triggered.
        
        Rule ID: {rule_id}
        Patient Data: {patient_data}
        
        Please provide:
        1. A clear explanation of why this alert was triggered
        2. The clinical significance
        3. Evidence-based recommendations
        4. Relevant guidelines or references
        
        Format the response in a way that would be helpful for a clinician.
        """

    def _generate_template_explanation(self, rule_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template-based explanation when LLM is not available."""
        templates = {
            "CKD_NSAID": {
                "explanation": "This patient has advanced chronic kidney disease and is prescribed an NSAID. According to KDIGO guidelines, NSAIDs should be avoided in this population due to the risk of renal function deterioration.",
                "confidence": 0.7,
                "references": ["KDIGO 2021 Clinical Practice Guideline"]
            },
            "QT_Prolongation": {
                "explanation": "This patient is at risk for QT prolongation due to medication interactions. Consider alternative medications or close monitoring.",
                "confidence": 0.7,
                "references": ["AHA/ACC Guidelines"]
            }
        }
        
        return templates.get(rule_id, {
            "explanation": "Alert triggered based on clinical rules.",
            "confidence": 0.5,
            "references": []
        })

    def _get_references(self, rule_id: str) -> list:
        """Get relevant clinical references for the rule."""
        references = {
            "CKD_NSAID": [
                "KDIGO 2021 Clinical Practice Guideline",
                "UpToDate: NSAIDs in CKD",
                "FDA Safety Communication: NSAIDs and Kidney Disease"
            ],
            "QT_Prolongation": [
                "AHA/ACC Guidelines for QT Prolongation",
                "CredibleMeds: QT Drug Lists",
                "FDA Drug Safety Communication: QT Prolongation"
            ]
        }
        return references.get(rule_id, [])

# Example usage:
# explainer = LLMExplainer()
# explanation = await explainer.explain("rule123", patient)
# print(explanation)
