import numpy as np
import shap
from typing import Dict, Any, List, Tuple
import logging
from models import RuleMatch, ClinicalRule
import json

logger = logging.getLogger(__name__)

class RuleExplainer:
    def __init__(self):
        self.feature_names = []
        # Do not initialize self.explainer here

    def explain_rule_match(
        self,
        rule: ClinicalRule,
        patient_data: Dict[str, Any],
        match_result: RuleMatch
    ) -> Dict[str, Any]:
        """
        Generate SHAP-based explanation for a rule match
        Time Complexity: O(n) where n is number of features
        Space Complexity: O(n) for storing feature values
        """
        try:
            # Convert patient data to feature vector
            features = self._extract_features(patient_data, rule)

            # Calculate SHAP values
            shap_values = self._calculate_shap_values(features, rule)

            # Generate visualization data
            visualization = self._generate_visualization(shap_values, features)

            # Create explanation summary
            explanation = self._create_explanation(shap_values, features, rule)

            return {
                "explanation": explanation,
                "visualization": visualization,
                "confidence_score": match_result.confidence_score,
                "feature_importance": self._get_feature_importance(shap_values)
            }

        except Exception as e:
            logger.error(f"Error generating rule explanation: {str(e)}")
            return self._generate_fallback_explanation(rule, match_result)

    def _extract_features(
        self,
        patient_data: Dict[str, Any],
        rule: ClinicalRule
    ) -> np.ndarray:
        features = []
        self.feature_names = []
        for condition in rule.conditions:
            if condition["type"] == "lab":
                value = self._get_lab_value(patient_data, condition["code"])
                features.append(value)
                self.feature_names.append(condition["code"])
            elif condition["type"] == "medication":
                value = self._get_medication_value(patient_data, condition["code"])
                features.append(value)
                self.feature_names.append(condition["code"])
            elif condition["type"] == "condition":
                value = self._get_condition_value(patient_data, condition["code"])
                features.append(value)
                self.feature_names.append(condition["code"])
        return np.array(features)

    def _calculate_shap_values(
        self,
        features: np.ndarray,
        rule: ClinicalRule
    ) -> np.ndarray:
        # Create a simple rule-based model for SHAP
        def rule_model(x):
            return np.array([self._evaluate_rule(x, rule)])

        # Initialize explainer only when needed
        explainer = shap.Explainer(rule_model, feature_names=self.feature_names)
        return explainer.shap_values(features)

    def _generate_visualization(
        self,
        shap_values: np.ndarray,
        features: np.ndarray
    ) -> Dict[str, Any]:
        return {
            "type": "shap_summary",
            "values": shap_values.tolist(),
            "features": features.tolist(),
            "feature_names": self.feature_names
        }

    def _create_explanation(
        self,
        shap_values: np.ndarray,
        features: np.ndarray,
        rule: ClinicalRule
    ) -> str:
        top_features = self._get_top_features(shap_values, features)
        explanation = f"This alert was triggered because:\n"
        for feature, value, importance in top_features:
            explanation += f"- {feature} ({value}) contributed {importance:.1%} to the decision\n"
        return explanation

    def _get_feature_importance(
        self,
        shap_values: np.ndarray
    ) -> List[Dict[str, Any]]:
        return [
            {
                "feature": name,
                "importance": float(value)
            }
            for name, value in zip(self.feature_names, np.abs(shap_values))
        ]

    def _get_top_features(
        self,
        shap_values: np.ndarray,
        features: np.ndarray,
        top_n: int = 3
    ) -> List[Tuple[str, float, float]]:
        abs_values = np.abs(shap_values)
        top_indices = np.argsort(abs_values)[-top_n:][::-1]
        return [
            (
                self.feature_names[i],
                float(features[i]),
                float(abs_values[i])
            )
            for i in top_indices
        ]

    def _evaluate_rule(self, features: np.ndarray, rule: ClinicalRule) -> float:
        confidence = 1.0
        for i, condition in enumerate(rule.conditions):
            if not self._check_condition(features[i], condition):
                confidence *= 0.5
        return confidence

    def _check_condition(self, value: float, condition: Dict[str, Any]) -> bool:
        if condition["operator"] == ">":
            return value > condition["value"]
        elif condition["operator"] == "<":
            return value < condition["value"]
        elif condition["operator"] == "=":
            return value == condition["value"]
        return False

    def _generate_fallback_explanation(
        self,
        rule: ClinicalRule,
        match_result: RuleMatch
    ) -> Dict[str, Any]:
        return {
            "explanation": match_result.explanation,
            "visualization": None,
            "confidence_score": match_result.confidence_score,
            "feature_importance": []
        }

    def _get_lab_value(self, patient_data: Dict[str, Any], code: str) -> float:
        for obs in patient_data.get("observations", []):
            if obs["code"] == code:
                return float(obs["value"])
        return 0.0

    def _get_medication_value(self, patient_data: Dict[str, Any], code: str) -> float:
        for med in patient_data.get("medications", []):
            if med["code"] == code:
                return 1.0
        return 0.0

    def _get_condition_value(self, patient_data: Dict[str, Any], code: str) -> float:
        for cond in patient_data.get("conditions", []):
            if cond["code"] == code:
                return 1.0
        return 0.0 