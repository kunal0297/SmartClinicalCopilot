# backend/llm_explainer.py

import os
import openai
from models import Patient

openai.api_key = os.getenv("OPENAI_API_KEY")

class LLMExplainer:
    def __init__(self):
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def explain(self, rule_id: str, patient: Patient) -> str:
        prompt = (
            f"Explain the clinical rule with ID {rule_id} "
            f"for the following patient data:\n{patient.json()}"
        )
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=200,
                temperature=0.7,
                n=1,
                stop=None,
            )
            explanation = response.choices[0].text.strip()
            return explanation
        except Exception as e:
            return f"Failed to get explanation: {str(e)}"
