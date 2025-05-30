import logging
from typing import Dict, List, Any, Optional
# import yaml
# from pathlib import Path
# import json
from datetime import datetime, timedelta
# from durable.rules import Engine, KnowledgeBase
from experta import *

logger = logging.getLogger(__name__)

class BloodPressureFact(Fact):
    """Fact representing a blood pressure reading"""
    systolic = Field(int, mandatory=True)
    diastolic = Field(int, mandatory=True)
    timestamp = Field(datetime, mandatory=True)

class MedicationFact(Fact):
    """Fact representing a medication"""
    name = Field(str, mandatory=True)
    dosage = Field(str, mandatory=True)
    frequency = Field(str, mandatory=True)
    start_date = Field(datetime, mandatory=True)

class ConditionFact(Fact):
    """Fact representing a medical condition"""
    name = Field(str, mandatory=True)
    status = Field(str, mandatory=True)
    onset_date = Field(datetime, mandatory=True)

class AlertFact(Fact):
    """Fact representing an alert"""
    type = Field(str, mandatory=True)
    severity = Field(str, mandatory=True)
    message = Field(str, mandatory=True)
    recommendations = Field(list, mandatory=True)

# Refactored to use experta
class RulesEngine(KnowledgeEngine):
    # You will need to define your rules here as methods using the @Rule decorator
    # For example:
    # @Rule(Fact(status='critical'))
    # def critical_status_rule(self, fact):
    #     print("Detected critical status!")
    #     # You can assert new facts or perform actions here

    def __init__(self, config_path: str = "config/self_healing_config.yaml"):
        super().__init__()
        self.alerts = []
        logger.info("Experta Rules engine initialized. Add your rules as @Rule methods.")

    def reset(self):
        """Reset the engine state"""
        super().reset()
        self.alerts = []

    def run(self, steps=None):
        """Run the rules engine"""
        try:
            super().run(steps)
        except Exception as e:
            logger.error(f"Error running rules engine: {str(e)}")
            return []

    # The evaluate method now uses experta's declare and run methods
    def evaluate(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            # Reset engine state
            self.reset()

            # Declare facts
            for fact in facts:
                if "systolic" in fact:
                    self.declare(BloodPressureFact(**fact))
                elif "name" in fact and "dosage" in fact:
                    self.declare(MedicationFact(**fact))
                elif "name" in fact and "status" in fact:
                    self.declare(ConditionFact(**fact))

            # Run rules
            self.run()

            return self.alerts
        except Exception as e:
            logger.error(f"Error evaluating rules: {str(e)}")
            return []

    @Rule(
        BloodPressureFact(systolic=P(lambda x: x > 140)),
        BloodPressureFact(systolic=P(lambda x: x > 140)),
        BloodPressureFact(systolic=P(lambda x: x > 140))
    )
    def high_blood_pressure_rule(self):
        """Rule for detecting consistently high blood pressure"""
        self.alerts.append({
            "type": "blood_pressure",
            "severity": "high",
            "message": "Patient has shown consistently high blood pressure readings",
            "recommendations": [
                "Consider immediate blood pressure medication adjustment",
                "Schedule follow-up appointment",
                "Monitor for symptoms of hypertensive crisis"
            ]
        })

    @Rule(
        MedicationFact(name="lisinopril"),
        BloodPressureFact(systolic=P(lambda x: x > 160))
    )
    def medication_adjustment_rule(self):
        """Rule for detecting need for medication adjustment"""
        self.alerts.append({
            "type": "medication",
            "severity": "high",
            "message": "Blood pressure remains high despite current medication",
            "recommendations": [
                "Consider increasing lisinopril dosage",
                "Evaluate for additional antihypertensive medications",
                "Check for medication adherence"
            ]
        })

    @Rule(
        ConditionFact(name="hypertension"),
        BloodPressureFact(systolic=P(lambda x: x > 180))
    )
    def hypertensive_crisis_rule(self):
        """Rule for detecting hypertensive crisis"""
        self.alerts.append({
            "type": "crisis",
            "severity": "critical",
            "message": "Potential hypertensive crisis detected",
            "recommendations": [
                "Immediate medical attention required",
                "Consider emergency department visit",
                "Monitor for symptoms of end-organ damage"
            ]
        })

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts"""
        return self.alerts

    # The add_rule and remove_rule methods are not applicable in experta's typical use case
    # where rules are defined as methods.
    # If dynamic rule management is critical, a different approach would be needed with experta,
    # potentially involving modifying the KnowledgeEngine class definition at runtime, which is complex.
    # Leaving placeholder methods or removing them based on necessity.
    # def add_rule(self, rule: Dict[str, Any]):
    #     logger.warning("add_rule is not directly supported in this experta implementation.")
    #     pass

    # def remove_rule(self, rule_id: str):
    #     logger.warning("remove_rule is not directly supported in this experta implementation.")
    #     pass