import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
print("Script started")
print("sys.path at startup:", sys.path)

from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import time # Added time import
import os # Added os import
from dotenv import load_dotenv # Added dotenv import
from tenacity import retry, stop_after_attempt, wait_exponential # Added tenacity imports
from prometheus_client import Counter, Histogram, generate_latest # Added prometheus imports
from prometheus_fastapi_instrumentator import Instrumentator # Added instrumentator import
import json # Added json import

from backend.database import get_db, engine, SessionLocal
from backend.models import Base, Patient as ModelPatient, Alert as ModelAlert, ClinicalRule, RuleCondition, RuleAction, RuleExplanation, SeverityLevel, Feedback as ModelFeedback, Condition as ModelCondition, Observation as ModelObservation, PatientConditions as ModelPatientConditions
from backend.schemas import (
    ClinicalRule as SchemaClinicalRule,
    Alert as SchemaAlert,
    Patient as SchemaPatient,
    RuleMatch,
    AlertOverride,
    ClinicalScore,
    Feedback as SchemaFeedback
)
from backend.routers import patients
from backend.rules_engine import RulesEngine
from backend.fhir_client import FHIRClient
from backend.llm_service import LLMService, LLMExplainer
from backend.monitoring import AlertMetricsService
from backend.error_handler import ErrorHandler
from backend.config import settings
from backend.logging_config import setup_logging, LogContext
from backend.rule_loader import RuleLoader
from backend.feedback import FeedbackSystem
from backend.smart_launch import router as smart_router
from backend.explainability import RuleExplainer
from backend.trie_engine import TrieEngine

# Setup logging
setup_logging()
# logger = logging.getLogger(__name__)
import logging # Added import logging here if not already present globally
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Smart Clinical Copilot",
    description="AI-powered clinical decision support system",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Initialize error handler
error_handler = ErrorHandler()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Add error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    with LogContext(
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else None
    ):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await error_handler.handle_exception(request, exc)

# Add exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await error_handler.handle_exception(request, exc)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    with LogContext(endpoint="/health"):
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": app.version,
            "environment": settings.ENVIRONMENT
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
                "count": len(RuleLoader("rules").load_rules()) # Use RuleLoader directly if not initialized as service yet
            },
            "fhir": {
                "status": "healthy" # Assuming FHIRClient is always healthy if initialized
            },
            "llm": {
                "status": "healthy" # Assuming LLMService/LLMExplainer is always healthy if initialized
            },
            "smart": {
                "status": "healthy" # Assuming smart_router is always healthy if imported
            }
        }
    }
    return health_status

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Error metrics endpoint
@app.get("/metrics/errors")
async def get_error_metrics():
    with LogContext(endpoint="/metrics/errors"):
        return error_handler.get_error_metrics()

# Initialize services (ensure these are initialized after app)
rules_engine = RulesEngine()
fhir_client = FHIRClient()
llm_service = LLMService()
alert_metrics = AlertMetricsService()
llm_explainer = LLMExplainer() # Initialize LLMExplainer
rule_loader = RuleLoader("rules") # Initialize RuleLoader
feedback_system = FeedbackSystem() # Initialize FeedbackSystem
trie_engine = TrieEngine() # Initialize TrieEngine
rule_explainer = RuleExplainer() # Initialize RuleExplainer

# Load rules on startup
@app.on_event("startup")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def startup_event():
    try:
        rules = rule_loader.load_rules()
        for rule in rules:
            trie_engine.add_rule(rule)
    except Exception as e:
        logger.error(f"Failed to load rules: {str(e)}")
        raise

# API endpoints
@app.get("/")
async def root():
    with LogContext(endpoint="/"):
        return {
            "message": "Welcome to Smart Clinical Copilot API",
            "version": app.version,
            "documentation": "/docs",
            "health": "/health"
        }

@app.post("/match-rules", response_model=List[SchemaAlert]) # Using schema Alert
async def match_rules(patient: SchemaPatient): # Using schema Patient
    with LogContext(endpoint="/match-rules", method="POST", patient_id=patient.id):
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
                        feedback_stats = {} # Assuming feedback_stats is collected elsewhere or from feedback_system
                        alerts.append(SchemaAlert(
                            rule_id=getattr(rule, 'id', rule.get('id', '')),
                            message=getattr(rule.actions[0], 'message', rule.actions[0].get('message', '')),
                            severity=getattr(rule, 'severity', rule.get('severity', 'warning')),
                            triggered_by=triggered_by,
                            explanation=explanation,
                            shap_explanation=shap_explanation,
                            feedback_stats=feedback_stats
                        ))
                except Exception as rule_error:
                    rule_id = getattr(rule, 'id', rule.get('id', 'unknown'))
                    logger.error(f"Error processing rule {rule_id}: {rule_error}", exc_info=True)
                    # Depending on desired behavior, you might want to add a failed alert or just log
                    continue # Continue to the next rule
            return alerts
        except Exception as e:
            logger.error(f"Error matching rules: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-rule", response_model=RuleExplanation)
async def explain_rule(rule_id: str, patient: SchemaPatient):
     with LogContext(endpoint="/explain-rule", method="POST", rule_id=rule_id, patient_id=patient.id):
        try:
            # Get LLM explanation
            explanation = await llm_explainer.explain(rule_id, patient.model_dump())

            # Get SHAP-based explanation
            rule = next((r for r in rule_loader.load_rules() if r.id == rule_id), None)
            if rule:
                # Assuming RuleMatch schema and explain_rule_match function are compatible
                shap_explanation = rule_explainer.explain_rule_match(
                    rule,
                    patient.model_dump(),
                    RuleMatch(
                        patient_id=patient.id,
                        rule_id=rule_id,
                        confidence_score=0.95, # Placeholder confidence score
                        explanation=explanation # Use LLM explanation here
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
            logger.error(f"Error explaining rule {rule_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to explain rule: {str(e)}")

@app.get("/suggest-rules")
async def suggest_rules(prefix: str):
    with LogContext(endpoint="/suggest-rules", method="GET", prefix=prefix):
        try:
            suggestions = trie_engine.search(prefix)
            return {"suggestions": suggestions}
        except Exception as e:
            logger.error(f"Error suggesting rules for prefix {prefix}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to suggest rules: {str(e)}")

@app.post("/feedback", response_model=Dict[str, Any]) # Assuming feedback endpoint returns a dict
async def submit_feedback(feedback: SchemaFeedback, db: Session = Depends(get_db)):
    with LogContext(endpoint="/feedback", method="POST", alert_id=feedback.alert_id, rule_id=feedback.rule_id):
        try:
            # Assuming feedback_system.record_feedback handles database interaction or returns a dict
            result = await feedback_system.record_feedback(
                feedback.alert_id,
                feedback.rule_id,
                feedback.helpful,
                feedback.comments,
                db=db # Pass db session if needed by feedback_system
            )
            return result # Return whatever feedback_system.record_feedback returns
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.get("/feedback/{rule_id}", response_model=List[SchemaFeedback]) # Assuming this returns a list of feedback schemas
async def get_rule_feedback(rule_id: str, db: Session = Depends(get_db)):
     with LogContext(endpoint="/feedback/{rule_id}", method="GET", rule_id=rule_id):
        try:
            # Assuming feedback_system.get_rule_feedback fetches from DB and returns list of dicts or models
            feedback_list = await feedback_system.get_rule_feedback(rule_id, db=db) # Pass db session
            # Convert results to Feedback schema if necessary
            return [SchemaFeedback(**f) for f in feedback_list] # Example conversion
        except Exception as e:
            logger.error(f"Error getting feedback for rule {rule_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")

@app.get("/feedback/recent", response_model=List[SchemaFeedback]) # Assuming this returns a list of feedback schemas
async def get_recent_feedback(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    with LogContext(endpoint="/feedback/recent", method="GET", limit=limit):
        try:
            # Assuming feedback_system.get_recent_feedback fetches from DB and returns list of dicts or models
            feedback_list = await feedback_system.get_recent_feedback(limit, db=db) # Pass db session
            # Convert results to Feedback schema if necessary
            return [SchemaFeedback(**f) for f in feedback_list] # Example conversion
        except Exception as e:
            logger.error(f"Error getting recent feedback (limit {limit}): {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve recent feedback: {str(e)}")

@app.get("/fhir-explorer/{resource_type}", response_model=List[Dict[str, Any]]) # Assuming list of dicts
async def fhir_explorer(resource_type: str, count: int = Query(10, ge=1, le=100)):
     with LogContext(endpoint="/fhir-explorer/{resource_type}", method="GET", resource_type=resource_type, count=count):
        try:
            # Assuming fhir_client.search_resources returns a list of dicts
            resources = fhir_client.search_resources(resource_type, params={"_count": count})
            return resources
        except Exception as e:
            logger.error(f"Error in fhir_explorer for resource type {resource_type}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to explore FHIR resources: {str(e)}")

@app.post("/patient-summary/{patient_id}", response_model=Dict[str, Any]) # Assuming summary is a dict
async def generate_patient_summary(patient_id: str):
     with LogContext(endpoint="/patient-summary/{patient_id}", method="POST", patient_id=patient_id):
        """
        Generate a comprehensive medical summary for a patient using AI.
        The summary is generated based on data from IRIS server and can use either
        local LLM or OpenAI depending on configuration.
        """
        try:
            # Assuming llm_explainer.generate_patient_summary returns a dict
            summary = await llm_explainer.generate_patient_summary(patient_id)
            return summary
        except Exception as e:
            logger.error(f"Error generating patient summary for {patient_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate patient summary: {str(e)}"
            )

@app.get("/patient-summaries/{patient_id}", response_model=List[Dict[str, Any]]) # Assuming returns list of dicts
async def get_patient_summaries(patient_id: str):
     with LogContext(endpoint="/patient-summaries/{patient_id}", method="GET", patient_id=patient_id):
        """
        Retrieve all stored AI-generated summaries for a patient.
        """
        try:
            # Assuming llm_explainer.iris_client.get_patient_summaries returns a list of dicts
            # Note: Accessing iris_client directly might need adjustment based on LLMExplainer structure
            summaries = await llm_explainer.iris_client.get_patient_summaries(patient_id)
            return summaries
        except Exception as e:
            logger.error(f"Error retrieving patient summaries for {patient_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve patient summaries: {str(e)}"
            )

@app.get("/demo-patients", response_model=List[SchemaPatient])
async def get_demo_patients():
    """Get a list of demo patients for testing."""
    try:
        demo_file = Path("demo_patients.json")
        if not demo_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo patients file not found"
            )
        
        with open(demo_file) as f:
            patients = json.load(f)
            return patients
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing demo patients file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading demo patients: {str(e)}"
        )

# Helper functions (moved from app.py)
def _check_lab_condition(observation: Any, condition: Dict[str, Any]) -> bool:
    """Check if a lab observation meets a condition"""
    # Ensure observation.value is treated as a float
    try:
        obs_value = float(observation.value)
        cond_value = float(condition["value"])
        if condition["operator"] == ">":
            return obs_value > cond_value
        elif condition["operator"] == "<":
            return obs_value < cond_value
        elif condition["operator"] == "=":
            return obs_value == cond_value
        # Add other operators if needed (>=, <=, !=)
    except (ValueError, TypeError) as e:
        logger.error(f"Error comparing lab value {observation.value} with condition {condition}: {e}", exc_info=True)
        return False # Cannot compare if values are not numeric
    return False

def _check_med_condition(medication: Any, condition: Dict[str, Any]) -> bool:
    """Check if a medication meets a condition"""
    # Assuming medication.code exists and condition["value"] is a list of codes
    med_code = getattr(medication, 'code', None)
    if med_code and isinstance(condition.get("value"), list):
         return med_code in condition["value"]
    logger.warning(f"Could not check medication condition: medication code {med_code}, condition value type {type(condition.get('value'))}")
    return False

def _check_condition(condition_obj: Any, condition: Dict[str, Any]) -> bool:
    """Check if a condition meets a condition"""
     # Assuming condition_obj.code exists and condition["code"] is a specific code
    obj_code = getattr(condition_obj, 'code', None)
    if obj_code and condition.get("code") is not None:
         return obj_code == condition["code"]
    logger.warning(f"Could not check condition: object code {obj_code}, condition code {condition.get('code')}")
    return False

# Include the new patients router
app.include_router(patients.router)

# Include the SMART on FHIR router
app.include_router(smart_router, prefix="/smart", tags=["SMART on FHIR"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG_MODE
    ) 