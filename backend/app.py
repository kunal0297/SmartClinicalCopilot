from fastapi import FastAPI, HTTPException, Depends, Request
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

from models import (
    Patient, Alert, Rule, RuleCondition, RuleAction,
    RuleExplanation, SeverityLevel, Feedback
)
from fhir_client import FHIRClient
from llm_explainer import LLMExplainer
from trie_engine import TrieEngine
from rule_loader import RuleLoader
from feedback import FeedbackSystem

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
            triggered = False
            triggered_by = []
            
            for condition in rule.conditions:
                if condition["type"] == "lab":
                    for obs in patient.conditions.observations:
                        if obs.code == condition["code"]:
                            if _check_lab_condition(obs, condition):
                                triggered = True
                                triggered_by.append(f"{obs.display}: {obs.value} {obs.unit}")
                
                elif condition["type"] == "medication":
                    for med in patient.conditions.medications:
                        if med.code == condition["code"]:
                            if _check_med_condition(med, condition):
                                triggered = True
                                triggered_by.append(f"{med.display}")
                
                elif condition["type"] == "condition":
                    for cond in patient.conditions.conditions:
                        if cond.code == condition["code"]:
                            if _check_condition(cond, condition):
                                triggered = True
                                triggered_by.append(f"{cond.display}")
            
            if triggered:
                # Get LLM explanation
                explanation = await llm_explainer.explain(rule.id, patient.dict())
                
                # Get feedback statistics
                feedback_stats = await feedback_system.get_rule_feedback(rule.id)
                
                alerts.append(Alert(
                    rule_id=rule.id,
                    message=rule.actions[0]["message"],
                    severity=rule.severity,
                    triggered_by=triggered_by,
                    explanation=explanation,
                    feedback_stats=feedback_stats
                ))
        
        return alerts
    
    except Exception as e:
        logger.error(f"Error matching rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-rule", response_model=RuleExplanation)
async def explain_rule(rule_id: str, patient: Patient):
    try:
        explanation = await llm_explainer.explain(rule_id, patient.dict())
        return explanation
    except Exception as e:
        logger.error(f"Error explaining rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    try:
        patient_data = await fhir_client.get_patient(patient_id)
        return patient_data
    except Exception as e:
        logger.error(f"Error fetching patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        logger.error(f"Error getting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/recent")
async def get_recent_feedback(limit: int = 10):
    try:
        feedback = await feedback_system.get_recent_feedback(limit)
        return feedback
    except Exception as e:
        logger.error(f"Error getting recent feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _check_lab_condition(observation: Any, condition: Dict[str, Any]) -> bool:
    if condition["operator"] == "<":
        return observation.value < condition["value"]
    elif condition["operator"] == ">":
        return observation.value > condition["value"]
    elif condition["operator"] == "<=":
        return observation.value <= condition["value"]
    elif condition["operator"] == ">=":
        return observation.value >= condition["value"]
    elif condition["operator"] in ["=", "=="]:
        return observation.value == condition["value"]
    elif condition["operator"] == "!=":
        return observation.value != condition["value"]
    return False

def _check_med_condition(medication: Any, condition: Dict[str, Any]) -> bool:
    if condition["operator"] == "=":
        return medication.status == condition["value"]
    return False

def _check_condition(condition_obj: Any, condition: Dict[str, Any]) -> bool:
    if condition["operator"] == "=":
        return condition_obj.status == condition["value"]
    return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
