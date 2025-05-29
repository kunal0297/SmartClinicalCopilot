from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import json
from datetime import datetime

from models import (
    Patient, Alert, ClinicalRule, RuleCondition, RuleAction,
    RuleExplanation, SeverityLevel, Feedback, Condition, Observation, PatientConditions
)
from fhir_client import FHIRClient
from llm_explainer import LLMExplainer
from trie_engine import TrieEngine
from rule_loader import RuleLoader
from feedback import FeedbackSystem
from smart_launch import router as smart_router
from explainability import RuleExplainer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Clinical Decision Support System",
    description="API for clinical rule matching and explanation services",
    version="1.0.0"
)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Initialize services
fhir_client = FHIRClient()
llm_explainer = LLMExplainer()
trie_engine = TrieEngine()
rule_loader = RuleLoader("rules")
feedback_system = FeedbackSystem()
rule_explainer = RuleExplainer()

# Include SMART on FHIR router
app.include_router(smart_router, prefix="/smart", tags=["SMART on FHIR"])

# Load rules with retry mechanism
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def load_rules():
    try:
        rules = rule_loader.load_rules()
        for rule in rules:
            trie_engine.add_rule(rule)
        return rules
    except Exception as e:
        logger.error(f"Error loading rules: {str(e)}")
        raise

# Load rules on startup
@app.on_event("startup")
async def startup_event():
    try:
        load_rules()
    except Exception as e:
        logger.error(f"Failed to load rules: {str(e)}")

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/health/detailed")
async def detailed_health_check():
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "components": {
            "rules": {
                "status": "healthy",
                "count": len(rule_loader.load_rules())
            },
            "fhir": {
                "status": "healthy" if fhir_client else "unhealthy"
            },
            "llm": {
                "status": "healthy" if llm_explainer else "unhealthy"
            },
            "smart": {
                "status": "healthy" if smart_router else "unhealthy"
            }
        }
    }
    return health_status

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# API endpoints
@app.get("/")
async def root():
    return {
        "name": "Clinical Decision Support System",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/match-rules", response_model=List[Alert])
async def match_rules(patient: Patient):
    try:
        alerts = []
        rules = rule_loader.load_rules()
        for rule in rules:
            try:
                triggered = False
                triggered_by = []
                # Defensive: support both object and dict
                conditions = getattr(rule, "conditions", None) or rule.get("conditions", [])
                for condition in conditions:
                    c_type = getattr(condition, "type", None) or condition.get("type", None)
                    c_code = getattr(condition, "code", None) or condition.get("code", None)
                    if c_type == "lab":
                        for obs in patient.conditions.observations:
                            if obs.code == c_code:
                                if _check_lab_condition(obs, condition):
                                    triggered = True
                                    triggered_by.append(f"{obs.display}: {obs.value} {obs.unit}")
                    elif c_type == "medication":
                        for med in patient.conditions.medications:
                            if med.code == c_code:
                                if _check_med_condition(med, condition):
                                    triggered = True
                                    triggered_by.append(f"{med.display}")
                    elif c_type == "condition":
                        for cond in patient.conditions.conditions:
                            if cond.code == c_code:
                                if _check_condition(cond, condition):
                                    triggered = True
                                    triggered_by.append(f"{cond.display}")
                if triggered:
                    # Get LLM explanation (skip if no API key)
                    explanation = "LLM explanation not available (no API key)"
                    shap_explanation = None
                    feedback_stats = {}
                    alerts.append(Alert(
                        rule_id=getattr(rule, 'id', rule.get('id', '')),
                        message=getattr(rule.actions[0], 'message', rule.actions[0].get('message', '')),
                        severity=getattr(rule, 'severity', rule.get('severity', 'warning')),
                        triggered_by=triggered_by,
                        explanation=explanation,
                        shap_explanation=shap_explanation,
                        feedback_stats=feedback_stats
                    ))
            except Exception as rule_error:
                logger.error(f"Error processing rule {getattr(rule, 'id', rule.get('id', 'unknown'))}: {rule_error}")
                continue
        return alerts
    except Exception as e:
        logger.error(f"Error matching rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-rule", response_model=RuleExplanation)
async def explain_rule(rule_id: str, patient: Patient):
    try:
        # Get LLM explanation
        explanation = await llm_explainer.explain(rule_id, patient.dict())
        
        # Get SHAP-based explanation
        rule = next((r for r in rule_loader.load_rules() if r.id == rule_id), None)
        if rule:
            shap_explanation = rule_explainer.explain_rule_match(
                rule,
                patient.dict(),
                RuleMatch(
                    patient_id=patient.id,
                    rule_id=rule_id,
                    confidence_score=0.95,
                    explanation=explanation
                )
            )
        else:
            shap_explanation = None
        
        return RuleExplanation(
            rule_id=rule_id,
            explanation=explanation,
            shap_explanation=shap_explanation
        )
    except Exception as e:
        logger.error(f"Error explaining rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def load_demo_patients():
    with open("demo_patients.json", "r") as f:
        return json.load(f)

def save_demo_patients(patients):
    with open("demo_patients.json", "w") as f:
        json.dump(patients, f, indent=2)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return None

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    try:
        # Serve demo patient if id starts with 'demo-'
        if patient_id.startswith("demo-"):
            demo_patients = load_demo_patients()
            patient_data = next((p for p in demo_patients if p["id"] == patient_id), None)
            if not patient_data:
                raise HTTPException(status_code=404, detail="Demo patient not found")
            name = patient_data.get("name", [{}])[0]
            # Ensure 'given' is a string, not a list
            given_val = name.get("given", "")
            if isinstance(given_val, list):
                given_val = given_val[0] if given_val else ""
            name_list = [{
                "given": given_val,
                "family": name.get("family", "")
            }]
            birth_date = parse_date(patient_data.get("birthDate", None))
            conditions = [
                Condition(
                    code=cond.get("code", {}).get("text", "N/A"),
                    system=cond.get("code", {}).get("system", ""),
                    display=cond.get("code", {}).get("text", "N/A"),
                    status=cond.get("clinicalStatus", {}).get("text", "N/A"),
                    onset=parse_date(cond.get("onsetDateTime", None))
                )
                for cond in patient_data.get("conditions", [])
            ]
            observations = [
                Observation(
                    code=obs.get("code", {}).get("text", "N/A"),
                    system=obs.get("code", {}).get("system", ""),
                    display=obs.get("code", {}).get("text", "N/A"),
                    value=obs.get("valueQuantity", {}).get("value", 0),
                    unit=obs.get("valueQuantity", {}).get("unit", ""),
                    date=parse_date(obs.get("effectiveDateTime", None))
                )
                for obs in patient_data.get("observations", [])
            ]
            medications = []
            patient = Patient(
                id=patient_data["id"],
                name=name_list,
                gender=patient_data.get("gender", "N/A"),
                birthDate=birth_date,
                conditions=PatientConditions(
                    medications=medications,
                    observations=observations,
                    conditions=conditions
                )
            )
            return patient
        # Get real patient data from IRIS Health
        patient_data = await fhir_client.get_patient_data(patient_id)
        if not patient_data:
            # Fallback: serve demo patient if exists
            demo_patients = load_demo_patients()
            patient_data = next((p for p in demo_patients if p["id"] == patient_id), None)
            if not patient_data:
                raise HTTPException(status_code=404, detail="Patient not found")
            patient = Patient(
                id=patient_data["id"],
                demographics={
                    "name": patient_data["name"],
                    "gender": patient_data["gender"],
                    "birthDate": patient_data["birthDate"]
                },
                conditions={
                    "medications": [],
                    "observations": patient_data.get("observations", []),
                    "conditions": patient_data.get("conditions", [])
                }
            )
            return patient
        # Convert FHIR data to our Patient model
        patient = Patient(
            id=patient_data["id"],
            demographics=patient_data["demographics"],
            conditions={
                "medications": patient_data["medications"],
                "observations": patient_data["labs"],
                "conditions": patient_data["conditions"]
            }
        )
        return patient
    except Exception as e:
        logger.error(f"Error getting patient data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo-patients")
async def list_demo_patients():
    return load_demo_patients()

@app.post("/demo-patients")
async def create_demo_patient(patient: dict):
    demo_patients = load_demo_patients()
    demo_patients.append(patient)
    save_demo_patients(demo_patients)
    return {"status": "created", "patient": patient}

@app.put("/demo-patients/{patient_id}")
async def update_demo_patient(patient_id: str, patient: dict):
    demo_patients = load_demo_patients()
    for i, p in enumerate(demo_patients):
        if p["id"] == patient_id:
            demo_patients[i] = patient
            save_demo_patients(demo_patients)
            return {"status": "updated", "patient": patient}
    raise HTTPException(status_code=404, detail="Demo patient not found")

@app.delete("/demo-patients/{patient_id}")
async def delete_demo_patient(patient_id: str):
    demo_patients = load_demo_patients()
    demo_patients = [p for p in demo_patients if p["id"] != patient_id]
    save_demo_patients(demo_patients)
    return {"status": "deleted", "patient_id": patient_id}

@app.get("/suggest-rules")
async def suggest_rules(prefix: str):
    try:
        suggestions = trie_engine.search(prefix)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error suggesting rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    try:
        result = await feedback_system.record_feedback(
            feedback.alert_id,
            feedback.rule_id,
            feedback.helpful,
            feedback.comments
        )
        return result
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/{rule_id}")
async def get_rule_feedback(rule_id: str):
    try:
        feedback = await feedback_system.get_rule_feedback(rule_id)
        return feedback
    except Exception as e:
        logger.error(f"Error getting rule feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/recent")
async def get_recent_feedback(limit: int = 10):
    try:
        feedback = await feedback_system.get_recent_feedback(limit)
        return feedback
    except Exception as e:
        logger.error(f"Error getting recent feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fhir-explorer/{resource_type}")
async def fhir_explorer(resource_type: str, count: int = Query(10, ge=1, le=100)):
    """List FHIR resources of a given type from IRIS Health."""
    try:
        resources = fhir_client.search_resources(resource_type, params={"_count": count})
        return {"resources": resources}
    except Exception as e:
        logger.error(f"Error in fhir_explorer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cohort-analytics")
async def cohort_analytics():
    """Return basic cohort analytics (e.g., count of diabetics, hypertensives, etc.)."""
    try:
        # Example: count patients with diabetes and hypertension
        diabetics = fhir_client.search_resources("Condition", params={"code": "E11"})
        hypertensives = fhir_client.search_resources("Condition", params={"code": "I10"})
        return {
            "diabetics_count": len(diabetics),
            "hypertensives_count": len(hypertensives)
        }
    except Exception as e:
        logger.error(f"Error in cohort_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/patient-summary/{patient_id}")
async def generate_patient_summary(patient_id: str):
    """
    Generate a comprehensive medical summary for a patient using AI.
    The summary is generated based on data from IRIS server and can use either
    local LLM or OpenAI depending on configuration.
    """
    try:
        summary = await llm_explainer.generate_patient_summary(patient_id)
        return summary
    except Exception as e:
        logger.error(f"Error generating patient summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate patient summary: {str(e)}"
        )

@app.get("/patient-summaries/{patient_id}")
async def get_patient_summaries(patient_id: str):
    """
    Retrieve all stored AI-generated summaries for a patient.
    """
    try:
        summaries = await llm_explainer.iris_client.get_patient_summaries(patient_id)
        return summaries
    except Exception as e:
        logger.error(f"Error retrieving patient summaries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patient summaries: {str(e)}"
        )

# Helper functions
def _check_lab_condition(observation: Any, condition: Dict[str, Any]) -> bool:
    """Check if a lab observation meets a condition"""
    if condition["operator"] == ">":
        return float(observation.value) > float(condition["value"])
    elif condition["operator"] == "<":
        return float(observation.value) < float(condition["value"])
    elif condition["operator"] == "=":
        return float(observation.value) == float(condition["value"])
    return False

def _check_med_condition(medication: Any, condition: Dict[str, Any]) -> bool:
    """Check if a medication meets a condition"""
    return medication.code in condition["value"]

def _check_condition(condition_obj: Any, condition: Dict[str, Any]) -> bool:
    """Check if a condition meets a condition"""
    return condition_obj.code == condition["code"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
