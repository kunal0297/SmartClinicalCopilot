"""Lightweight forward-chaining clinical rules engine.

This module previously depended on ``experta`` which is not maintained for
modern Python versions (it pins ``frozendict==1.2`` and relies on
``collections.Mapping``). To keep the project installable and the engine
genuinely functional, it has been reimplemented in pure Python while keeping
the same public interface (``declare``/``reset``/``run``/``evaluate``/
``get_alerts``).
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Fact:
    """Base class for facts asserted into working memory."""

    data: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs: Any):
        self.data = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __contains__(self, key: str) -> bool:  # pragma: no cover - trivial
        return key in self.data


class BloodPressureFact(Fact):
    """Fact representing a blood pressure reading."""


class MedicationFact(Fact):
    """Fact representing a medication."""


class ConditionFact(Fact):
    """Fact representing a medical condition."""


class AlertFact(Fact):
    """Fact representing an alert."""


class RulesEngine:
    """A minimal forward-chaining rules engine for clinical facts.

    Rules are registered as ``(name, predicate, action)`` tuples. ``predicate``
    receives the current list of facts and returns ``True`` when the rule
    should fire; ``action`` receives the engine so it can append alerts.
    """

    def __init__(self, config_path: str = "config/self_healing_config.yaml"):
        self.config_path = config_path
        self.facts: List[Fact] = []
        self.alerts: List[Dict[str, Any]] = []
        self._rules: List[tuple] = []
        self._register_default_rules()
        logger.info("Pure-Python rules engine initialized with %d rules.", len(self._rules))

    # -- working memory -------------------------------------------------
    def declare(self, fact: Fact) -> None:
        """Assert a fact into working memory."""
        self.facts.append(fact)

    def reset(self) -> None:
        """Reset the engine state."""
        self.facts = []
        self.alerts = []

    # -- rule registration ----------------------------------------------
    def add_rule(self, name: str, predicate: Callable[[List[Fact]], bool],
                 action: Callable[["RulesEngine"], None]) -> None:
        self._rules.append((name, predicate, action))

    def remove_rule(self, name: str) -> None:
        self._rules = [r for r in self._rules if r[0] != name]

    # -- execution -------------------------------------------------------
    def run(self, steps: Optional[int] = None) -> List[Dict[str, Any]]:
        """Evaluate all registered rules against the current facts."""
        try:
            for name, predicate, action in self._rules:
                try:
                    if predicate(self.facts):
                        action(self)
                except Exception as rule_error:  # noqa: BLE001
                    logger.error("Error running rule %s: %s", name, rule_error)
            return self.alerts
        except Exception as e:  # noqa: BLE001
            logger.error("Error running rules engine: %s", e)
            return []

    def evaluate(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convenience helper: declare dict facts, run, return alerts."""
        try:
            self.reset()
            for fact in facts:
                if "systolic" in fact:
                    self.declare(BloodPressureFact(**fact))
                elif "name" in fact and "dosage" in fact:
                    self.declare(MedicationFact(**fact))
                elif "name" in fact and "status" in fact:
                    self.declare(ConditionFact(**fact))
            return self.run()
        except Exception as e:  # noqa: BLE001
            logger.error("Error evaluating rules: %s", e)
            return []

    def get_alerts(self) -> List[Dict[str, Any]]:
        return self.alerts

    # -- default clinical rules -----------------------------------------
    def _register_default_rules(self) -> None:
        def _bp_readings(facts: List[Fact]) -> List[BloodPressureFact]:
            return [f for f in facts if isinstance(f, BloodPressureFact)]

        def _high_bp(facts: List[Fact]) -> bool:
            high = [f for f in _bp_readings(facts) if int(f.get("systolic", 0)) > 140]
            return len(high) >= 3

        def _high_bp_action(engine: "RulesEngine") -> None:
            engine.alerts.append({
                "type": "blood_pressure",
                "severity": "high",
                "message": "Patient has shown consistently high blood pressure readings",
                "recommendations": [
                    "Consider immediate blood pressure medication adjustment",
                    "Schedule follow-up appointment",
                    "Monitor for symptoms of hypertensive crisis",
                ],
            })

        def _med_adjustment(facts: List[Fact]) -> bool:
            on_lisinopril = any(
                isinstance(f, MedicationFact) and f.get("name") == "lisinopril"
                for f in facts
            )
            severe_bp = any(
                isinstance(f, BloodPressureFact) and int(f.get("systolic", 0)) > 160
                for f in facts
            )
            return on_lisinopril and severe_bp

        def _med_adjustment_action(engine: "RulesEngine") -> None:
            engine.alerts.append({
                "type": "medication",
                "severity": "high",
                "message": "Blood pressure remains high despite current medication",
                "recommendations": [
                    "Consider increasing lisinopril dosage",
                    "Evaluate for additional antihypertensive medications",
                    "Check for medication adherence",
                ],
            })

        def _crisis(facts: List[Fact]) -> bool:
            has_htn = any(
                isinstance(f, ConditionFact) and f.get("name") == "hypertension"
                for f in facts
            )
            crisis_bp = any(
                isinstance(f, BloodPressureFact) and int(f.get("systolic", 0)) > 180
                for f in facts
            )
            return has_htn and crisis_bp

        def _crisis_action(engine: "RulesEngine") -> None:
            engine.alerts.append({
                "type": "crisis",
                "severity": "critical",
                "message": "Potential hypertensive crisis detected",
                "recommendations": [
                    "Immediate medical attention required",
                    "Consider emergency department visit",
                    "Monitor for symptoms of end-organ damage",
                ],
            })

        self.add_rule("high_blood_pressure", _high_bp, _high_bp_action)
        self.add_rule("medication_adjustment", _med_adjustment, _med_adjustment_action)
        self.add_rule("hypertensive_crisis", _crisis, _crisis_action)
