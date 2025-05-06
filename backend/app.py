from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fhir_client import FHIRClient
from llm_explainer import LLMExplainer
from trie_engine import TrieEngine
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
trie_engine = TrieEngine()

# Load rules into the trie engine
rule_loader = RuleLoader()
rules = rule_loader.load_rules()
trie_engine.build(rules)

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
        alerts = trie_engine.match(request.patient)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-rule", response_model=ExplanationResponse)
async def explain_rule(request: ExplanationRequest):
    """
    Explain a specific rule for a given patient.
    """
    try:
        explanation = llm_explainer.explain(request.rule_id, request.patient)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the FHIR Rules and LLM Services API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
