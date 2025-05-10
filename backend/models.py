from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Name(BaseModel):
    text: str

class Observation(BaseModel):
    code: str
    system: str
    display: str
    value: float
    unit: str
    date: Optional[datetime] = None

class Medication(BaseModel):
    code: str
    system: str
    display: str
    status: str
    intent: str
    date: Optional[datetime] = None

class Condition(BaseModel):
    code: str
    system: str
    display: str
    status: str
    onset: Optional[datetime] = None

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

    class Config:
        validate_assignment = True

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    rule_id = Column(Integer, ForeignKey("clinical_rules.id"))
    triggered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # e.g., "active", "overridden", "resolved"
    details = Column(JSON)
    
    rule = relationship("ClinicalRule")
    overrides = relationship("AlertOverride", back_populates="alert")

class AlertOverride(Base):
    __tablename__ = "alert_overrides"

    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    override_reason = Column(String)
    overridden_by = Column(String)  # User ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    alert = relationship("Alert", back_populates="overrides")

class ClinicalScore(Base):
    __tablename__ = "clinical_scores"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    score_type = Column(String)  # e.g., "CHA2DS2-VASc", "Wells"
    score_value = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    interpretation = Column(String)
    details = Column(JSON)

class RuleMatch(Base):
    __tablename__ = "rule_matches"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    rule_id = Column(Integer, ForeignKey("clinical_rules.id"))
    matched_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    explanation = Column(String)
    details = Column(JSON)
    
    rule = relationship("ClinicalRule")

class AlertMetrics(Base):
    __tablename__ = "alert_metrics"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    rule_id = Column(Integer, ForeignKey("clinical_rules.id"))
    alert_count = Column(Integer, default=0)
    override_count = Column(Integer, default=0)
    last_alert_at = Column(DateTime)
    last_override_at = Column(DateTime)
    
    rule = relationship("ClinicalRule")

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

class FeedbackStats(BaseModel):
    rule_id: str
    total_feedback: int
    helpful_count: int
    helpful_percentage: float

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

class Alert(BaseModel):
    rule_id: str
    message: str
    severity: SeverityLevel
    triggered_by: List[str]
    explanation: str
    shap_explanation: Optional[SHAPExplanation] = None
    feedback_stats: Optional[Dict[str, Any]] = None

class SMARTLaunchRequest(BaseModel):
    iss: str
    launch: str

class SMARTLaunchResponse(BaseModel):
    launch_url: str

class SMARTTokenResponse(BaseModel):
    access_token: str
    id_token: Dict[str, Any]
    patient: str
    scope: str

# Example usage:
# patient = Patient(id="12345", name=[HumanName(given=["John", "Doe"], family="Smith")])
# print(patient.json())
