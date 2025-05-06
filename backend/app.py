from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List
from fhir_client import FHIRClient
from llm_explainer import LLMExplainer
from rule_loader import RuleLoader
from models import Patient, Alert

# Initialize FastAPI app
app = FastAPI(title="FHIR Rules and LLM Services")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
fhir_client = FHIRClient()
llm_explainer = LLMExplainer()

# Load rules from directory
rule_loader = RuleLoader()
rules = rule_loader.load_rules()

# Pydantic models for request and response
class RuleRequest(BaseModel):
    patient: Patient

class ExplanationRequest(BaseModel):
    rule_id: str
    patient: Patient

class ExplanationResponse(BaseModel):
    explanation: str

@app.post("/match-rules", response_model=List[Alert])
async def match_rules(request: RuleRequest):
    """
    Match rules against a given patient.
    """
    try:
        patient = request.patient
        alerts = []

        # Search by rule text if provided in patient name
        if patient.name:
            name_entry = patient.name[0]
            if hasattr(name_entry, "text"):
                query = name_entry.text.lower()
                for rule in rules:
                    rule_id = rule.get("id")
                    rule_text = rule.get("text", "")
                    if rule_id and query in rule_text.lower():
                        alerts.append(Alert(rule_id=rule_id, message=rule_text))

        # Condition-based rule matching
        for rule in rules:
            rule_id = rule.get("id")
            conditions = rule.get("conditions", [])
            actions = rule.get("actions", [])
            match = True
            for cond in conditions:
                cond_type = cond.get("type")
                operator = cond.get("operator")
                value = cond.get("value")
                patient_val = getattr(patient, cond_type, None)
                if patient_val is None:
                    match = False
                    break
                try:
                    # Compare values
                    if operator == "<" and not (patient_val < value):
                        match = False
                        break
                    elif operator == ">" and not (patient_val > value):
                        match = False
                        break
                    elif operator in ("=", "==") and not (patient_val == value):
                        match = False
                        break
                    elif operator == "<=" and not (patient_val <= value):
                        match = False
                        break
                    elif operator == ">=" and not (patient_val >= value):
                        match = False
                        break
                    # Add other operators as needed
                except Exception:
                    match = False
                    break
            if match and rule_id:
                # Create alerts for each alert action
                for action in actions:
                    if action.get("type") == "alert":
                        message = action.get("message", "")
                        severity = action.get("severity")  # if exists
                        alerts.append(Alert(rule_id=rule_id, message=message, severity=severity))
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-rule", response_model=ExplanationResponse)
async def explain_rule(request: ExplanationRequest):
    """
    Explain a specific rule for a given patient.
    """
    try:
        explanation = await run_in_threadpool(llm_explainer.explain, request.rule_id, request.patient)
        return ExplanationResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """
    Retrieve a patient by ID from the FHIR server.
    """
    try:
        patient = await fhir_client.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., 404 from FHIR client)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the FHIR Rules and LLM Services API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
