from pydantic import BaseModel, validator, Field
from typing import List, Optional

class HumanName(BaseModel):
    given: Optional[List[str]] = Field(None, description="Given names (e.g., first, middle names)")
    family: Optional[str] = Field(None, description="Family name (e.g., last name)")
    use: Optional[str] = Field(None, description="Use of the name (e.g., 'official', 'nickname')")
    text: Optional[str] = Field(None, description="Combined text representation of the name")

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

class Patient(BaseModel):
    id: str = Field(..., description="Patient ID")
    name: Optional[List[HumanName]] = Field(None, description="Patient names")
    gender: Optional[str] = Field(None, description="Patient gender")
    birthDate: Optional[str] = Field(None, description="Patient date of birth in YYYY-MM-DD format")
    address: Optional[List[dict]] = Field(None, description="Patient addresses")
    maritalStatus: Optional[str] = Field(None, description="Patient marital status")
    eGFR: Optional[float] = Field(None, description="Estimated Glomerular Filtration Rate", gt=0, lt=200)
    QT_interval: Optional[float] = Field(None, description="QT Interval", gt=0, lt=1000)

    @validator("birthDate")
    def validate_birth_date(cls, value):
        if value and not isinstance(value, str):
            raise ValueError("Birth date must be a string")
        return value

    class Config:
        extra = "allow"
        validate_assignment = True

class Alert(BaseModel):
    rule_id: str = Field(..., description="ID of the triggered clinical rule")
    message: str = Field(..., description="Alert message describing the issue")
    severity: Optional[str] = Field("info", description="Severity level: info, warning, critical")
    triggered_by: Optional[List[str]] = Field(None, description="Fields or values that triggered the alert")

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

# Example usage:
# patient = Patient(id="12345", name=[HumanName(given=["John", "Doe"], family="Smith")])
# print(patient.json())
