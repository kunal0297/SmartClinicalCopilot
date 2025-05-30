from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Observation(BaseModel):
    code: str
    system: str
    display: str
    value: float
    unit: str
    date: Optional[datetime] = None

class Condition(BaseModel):
    code: str
    system: str
    display: str
    status: str
    onset: Optional[datetime] = None

class Medication(BaseModel):
    code: str
    system: str
    display: str
    status: str
    intent: str
    date: Optional[datetime] = None

class PatientConditions(BaseModel):
    observations: List[Observation] = []
    medications: List[Medication] = []
    conditions: List[Condition] = []

class Patient(BaseModel):
    id: str
    name: List[Dict[str, str]]
    gender: Optional[str] = None
    birthDate: Optional[datetime] = None
    conditions: PatientConditions

class RuleCondition(BaseModel):
    type: str
    code: str
    operator: str
    value: Any
    unit: Optional[str] = None

class RuleAction(BaseModel):
    type: str
    message: str
    severity: SeverityLevel
    explanation: Optional[Dict[str, Any]] = None

class ClinicalRule(BaseModel):
    id: str
    text: str
    category: str
    severity: SeverityLevel
    confidence: float
    conditions: List[RuleCondition]
    actions: List[RuleAction]

class RuleExplanation(BaseModel):
    rule_id: str
    explanation: str
    shap_explanation: Optional[Dict[str, Any]] = None

class Alert(BaseModel):
    id: Optional[int] = None
    patient_id: str
    rule_id: str
    triggered_at: Optional[datetime] = None
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    message: str
    severity: SeverityLevel
    triggered_by: List[str]
    explanation: str
    shap_explanation: Optional[Dict[str, Any]] = None
    feedback_stats: Optional[Dict[str, Any]] = None

class AlertOverride(BaseModel):
    id: Optional[int] = None
    alert_id: int
    override_reason: str
    overridden_by: str
    timestamp: Optional[datetime] = None

class ClinicalScore(BaseModel):
    id: Optional[int] = None
    patient_id: str
    score_type: str
    score_value: float
    calculated_at: Optional[datetime] = None
    interpretation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class RuleMatch(BaseModel):
    id: Optional[int] = None
    patient_id: str
    rule_id: str
    matched_at: Optional[datetime] = None
    confidence_score: float
    explanation: str
    details: Optional[Dict[str, Any]] = None

class AlertMetrics(BaseModel):
    id: Optional[int] = None
    patient_id: str
    rule_id: str
    alert_count: int = 0
    override_count: int = 0
    last_alert_at: Optional[datetime] = None
    last_override_at: Optional[datetime] = None

class Feedback(BaseModel):
    alert_id: str
    rule_id: str
    helpful: bool
    comments: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class SHAPExplanation(BaseModel):
    type: str = "shap_summary"
    values: List[float]
    features: List[float]
    feature_names: List[str]
    feature_importance: List[Dict[str, Any]] 