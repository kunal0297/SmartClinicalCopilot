from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging
from durable_rules import Engine, KnowledgeBase
from .models import ClinicalRule, RuleMatch, ClinicalScore

logger = logging.getLogger(__name__)

class RulesEngine:
    def __init__(self):
        self.engine = Engine()
        self.knowledge_base = KnowledgeBase()
        self._load_rules()

    def _load_rules(self):
        """Load clinical rules from the database"""
        # Example rules - in production, these would come from the database
        self.rules = [
            {
                "id": 1,
                "name": "NSAID CKD Contraindication",
                "guideline": "KDIGO 2021",
                "section": "4.3.1",
                "rule": """
                when
                    patient.egfr < 30 and
                    medication.type == "NSAID"
                then
                    raise_alert("NSAID contraindicated in CKD stage 4")
                """
            },
            {
                "id": 2,
                "name": "ACE Inhibitor Hyperkalemia",
                "guideline": "KDIGO 2021",
                "section": "4.2.1",
                "rule": """
                when
                    patient.potassium > 5.5 and
                    medication.type == "ACE Inhibitor"
                then
                    raise_alert("ACE inhibitor contraindicated with hyperkalemia")
                """
            },
            # Add more rules here
        ]

        # Load rules into the engine
        for rule in self.rules:
            self.engine.add_rule(rule["rule"])

    def evaluate_all(self, patient_data: Dict[str, Any]) -> List[RuleMatch]:
        """Evaluate all clinical rules for a patient"""
        matches = []
        
        try:
            # Convert patient data to facts
            facts = self._prepare_facts(patient_data)
            
            # Evaluate rules
            results = self.engine.evaluate(facts)
            
            # Process results
            for result in results:
                if result.get("alert"):
                    match = RuleMatch(
                        patient_id=patient_data["id"],
                        rule_id=result["rule_id"],
                        confidence_score=self._calculate_confidence(result),
                        explanation=self._generate_explanation(result),
                        details=result
                    )
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error evaluating rules: {str(e)}")
            raise

    def calculate_clinical_score(self, score_type: str, patient_data: Dict[str, Any]) -> ClinicalScore:
        """Calculate clinical scores (CHA₂DS₂-VASc, Wells, etc.)"""
        try:
            if score_type == "CHA2DS2-VASc":
                score = self._calculate_chads_vasc(patient_data)
            elif score_type == "Wells":
                score = self._calculate_wells_score(patient_data)
            else:
                raise ValueError(f"Unknown score type: {score_type}")
            
            return ClinicalScore(
                patient_id=patient_data["id"],
                score_type=score_type,
                score_value=score["total"],
                interpretation=score["interpretation"],
                details=score["details"]
            )
            
        except Exception as e:
            logger.error(f"Error calculating clinical score: {str(e)}")
            raise

    def _calculate_chads_vasc(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate CHA₂DS₂-VASc score"""
        score = 0
        details = {}
        
        # Age
        if patient_data.get("age", 0) >= 75:
            score += 2
            details["age"] = 2
        elif patient_data.get("age", 0) >= 65:
            score += 1
            details["age"] = 1
            
        # Sex
        if patient_data.get("sex") == "F":
            score += 1
            details["sex"] = 1
            
        # Other factors
        if patient_data.get("congestive_heart_failure"):
            score += 1
            details["chf"] = 1
        if patient_data.get("hypertension"):
            score += 1
            details["hypertension"] = 1
        if patient_data.get("diabetes"):
            score += 1
            details["diabetes"] = 1
        if patient_data.get("stroke_tia"):
            score += 2
            details["stroke_tia"] = 2
        if patient_data.get("vascular_disease"):
            score += 1
            details["vascular_disease"] = 1
            
        # Interpretation
        interpretation = self._interpret_chads_vasc(score)
        
        return {
            "total": score,
            "details": details,
            "interpretation": interpretation
        }

    def _calculate_wells_score(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Wells Score for DVT"""
        score = 0
        details = {}
        
        # Clinical symptoms
        if patient_data.get("active_cancer"):
            score += 1
            details["active_cancer"] = 1
        if patient_data.get("paralysis"):
            score += 1
            details["paralysis"] = 1
        if patient_data.get("recent_immobilization"):
            score += 1
            details["recent_immobilization"] = 1
        if patient_data.get("localized_tenderness"):
            score += 1
            details["localized_tenderness"] = 1
        if patient_data.get("entire_leg_swollen"):
            score += 1
            details["entire_leg_swollen"] = 1
        if patient_data.get("calf_swelling"):
            score += 1
            details["calf_swelling"] = 1
        if patient_data.get("pitting_edema"):
            score += 1
            details["pitting_edema"] = 1
        if patient_data.get("collateral_superficial_veins"):
            score += 1
            details["collateral_superficial_veins"] = 1
        if patient_data.get("alternative_diagnosis"):
            score -= 2
            details["alternative_diagnosis"] = -2
            
        # Interpretation
        interpretation = self._interpret_wells_score(score)
        
        return {
            "total": score,
            "details": details,
            "interpretation": interpretation
        }

    def _interpret_chads_vasc(self, score: int) -> str:
        """Interpret CHA₂DS₂-VASc score"""
        if score == 0:
            return "Low risk - No antithrombotic therapy recommended"
        elif score == 1:
            return "Low risk - Consider antithrombotic therapy"
        else:
            return "High risk - Anticoagulation recommended"

    def _interpret_wells_score(self, score: int) -> str:
        """Interpret Wells Score"""
        if score < 2:
            return "Low probability of DVT"
        elif score < 6:
            return "Moderate probability of DVT"
        else:
            return "High probability of DVT"

    def _prepare_facts(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert patient data to facts for rule engine"""
        return {
            "patient": patient_data,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for a rule match"""
        # In a real system, this would consider multiple factors
        return 0.95  # Example confidence score

    def _generate_explanation(self, result: Dict[str, Any]) -> str:
        """Generate human-readable explanation for a rule match"""
        rule = next((r for r in self.rules if r["id"] == result["rule_id"]), None)
        if rule:
            return f"According to {rule['guideline']} section {rule['section']}, {result['alert']}"
        return result["alert"] 