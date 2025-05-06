from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

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

class Alert(BaseModel):
    rule_id: str
    message: str
    severity: SeverityLevel
    triggered_by: List[str]
    explanation: Optional[RuleExplanation] = None
    feedback_stats: Optional[FeedbackStats] = None

class Rule(BaseModel):
    id: str
    text: str
    category: str
    severity: SeverityLevel
    confidence: float
    conditions: List[RuleCondition]
    actions: List[RuleAction]

    class Config:
        validate_assignment = True

class RuleCondition(BaseModel):
    type: str
    operator: str
    value: Any
    unit: Optional[str] = None
    source: str

    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['<', '>', '<=', '>=', '=', '==', '!=']
        if v not in valid_operators:
            raise ValueError(f'Invalid operator. Must be one of {valid_operators}')
        return v

class RuleAction(BaseModel):
    type: str
    message: str
    severity: Optional[SeverityLevel] = None
    references: Optional[List[Dict[str, str]]] = None

class RuleExplanation(BaseModel):
    rule_id: str
    explanation: str
    confidence: float
    references: List[str]

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

# Example usage:
# patient = Patient(id="12345", name=[HumanName(given=["John", "Doe"], family="Smith")])
# print(patient.json())
