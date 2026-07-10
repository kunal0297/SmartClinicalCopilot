import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# OpenAI is optional. Without it (or an API key) the explainer falls back to
# deterministic, guideline-based templates so the app works out of the box.
try:
    from openai import AsyncOpenAI
    _OPENAI_AVAILABLE = True
except Exception:  # noqa: BLE001
    AsyncOpenAI = None  # type: ignore
    _OPENAI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class LLMExplainer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        if not self.api_key:
            logger.warning("No OpenAI API key found. Explanations will be template-based only.")
        elif not _OPENAI_AVAILABLE:
            logger.warning("openai package not installed. Explanations will be template-based only.")
        else:
            self._client = AsyncOpenAI(api_key=self.api_key)
        # Lazily-created IRIS client for patient summaries; degrades gracefully.
        self._iris_client = None

    @property
    def iris_client(self):
        if self._iris_client is None:
            from backend.iris_client import IRISClient
            self._iris_client = IRISClient()
        return self._iris_client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def explain(self, rule_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an explanation for a triggered rule using LLM."""
        try:
            if not self._client:
                return self._generate_template_explanation(rule_id, patient_data)

            # Prepare the prompt
            prompt = self._create_prompt(rule_id, patient_data)

            # Call OpenAI API (v1 client)
            response = await self._client.chat.completions.create(
                model=self.model,
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

    async def generate_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate an AI patient summary, degrading gracefully without an LLM."""
        try:
            patient_data = await self.iris_client.get_patient_data(patient_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not fetch patient data for %s: %s", patient_id, e)
            patient_data = {"id": patient_id}

        if not self._client:
            summary_text = (
                f"Template summary for patient {patient_id}. "
                "Configure OPENAI_API_KEY or a local LLM (USE_LOCAL_LLM=true) for "
                "AI-generated narrative summaries."
            )
            model = "template"
        else:
            try:
                prompt = (
                    "Provide a concise clinical summary for the following patient "
                    f"data:\n{patient_data}"
                )
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a medical summarization assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=800,
                )
                summary_text = response.choices[0].message.content
                model = self.model
            except Exception as e:  # noqa: BLE001
                logger.error("LLM summary failed: %s", e)
                summary_text = f"Summary unavailable for patient {patient_id}: {e}"
                model = "error"

        summary = {
            "patient_id": patient_id,
            "summary": summary_text,
            "generated_at": datetime.now().isoformat(),
            "model": model,
        }
        try:
            await self.iris_client.store_patient_summary(patient_id, summary)
        except Exception as e:  # noqa: BLE001
            logger.debug("Could not persist patient summary: %s", e)
        return summary

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
