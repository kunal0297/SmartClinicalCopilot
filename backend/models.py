from pydantic import BaseModel
from typing import List, Optional

class HumanName(BaseModel):
    given: Optional[List[str]]
    family: Optional[str]

    class Config:
        extra = "allow"

class Patient(BaseModel):
    id: str
    name: Optional[List[HumanName]] = None
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    eGFR: Optional[float] = None
    QT_interval: Optional[float] = None

    class Config:
        extra = "allow"

class Alert(BaseModel):
    rule_id: str
    message: str
    severity: Optional[str] = None
