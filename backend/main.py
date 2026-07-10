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
                    conditions = getattr(rule, "conditions", None) or []
                    if not conditions:
                        continue

                    # A rule fires only when *all* of its conditions are satisfied.
                    all_met = True
                    triggered_by: List[str] = []
                    for condition in conditions:
                        met, evidence = _evaluate_condition(condition, patient)
                        if met:
                            if evidence:
                                triggered_by.append(evidence)
                        else:
                            all_met = False
                            break

                    if all_met:
                        actions = getattr(rule, "actions", []) or []
                        message = next(
                            (a.message for a in actions if getattr(a, "message", None)),
                            getattr(rule, "text", "Clinical rule triggered"),
                        )
                        severity = getattr(rule, "severity", None)
                        severity = severity.value if hasattr(severity, "value") else (severity or "warning")

                        # Deterministic explanation; upgraded to an LLM explanation
                        # automatically when an API key / local model is configured.
                        try:
                            explanation_result = await llm_explainer.explain(
                                getattr(rule, "id", ""), patient.model_dump()
                            )
                            explanation = explanation_result.get("explanation") if isinstance(
                                explanation_result, dict
                            ) else str(explanation_result)
                        except Exception:  # noqa: BLE001
                            explanation = getattr(rule, "text", "Clinical rule triggered")

                        alerts.append(SchemaAlert(
                            patient_id=patient.id,
                            rule_id=getattr(rule, "id", ""),
                            message=message,
                            severity=severity,
                            triggered_by=triggered_by,
                            explanation=explanation or "",
                        ))
                except Exception as rule_error:
                    rule_id = getattr(rule, "id", "unknown")
                    logger.error(f"Error processing rule {rule_id}: {rule_error}", exc_info=True)
                    continue
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

# Helper functions for rule evaluation --------------------------------------
def _compare_numeric(actual: float, operator: str, expected: float) -> bool:
    if operator in (">",):
        return actual > expected
    if operator in ("<",):
        return actual < expected
    if operator in (">=",):
        return actual >= expected
    if operator in ("<=",):
        return actual <= expected
    if operator in ("=", "=="):
        return actual == expected
    if operator in ("!=",):
        return actual != expected
    return False


def _matches_membership(code: str, operator: str, value: Any) -> bool:
    values = value if isinstance(value, (list, tuple, set)) else [value]
    values = [str(v).lower() for v in values]
    code = str(code).lower()
    if operator in ("in", "contains"):
        return code in values
    if operator == "not_in":
        return code not in values
    return code in values


def _evaluate_condition(condition: Any, patient: SchemaPatient):
    """Evaluate a single rule condition against a patient.

    Returns a ``(met, evidence)`` tuple where ``evidence`` is a human-readable
    description of the triggering finding (or ``None``).
    """
    c_type = getattr(condition, "type", None)
    operator = getattr(condition, "operator", None)
    value = getattr(condition, "value", None)

    pc = patient.conditions

    # Medication membership conditions
    if c_type == "medication":
        for med in pc.medications:
            candidates = [c for c in (med.code, med.display) if c]
            if any(_matches_membership(c, operator or "in", value) for c in candidates):
                return True, f"Medication: {med.display or med.code}"
        return False, None

    # Diagnosed-condition conditions
    if c_type == "condition":
        for cond in pc.conditions:
            candidates = [c for c in (cond.code, cond.display) if c]
            if any(_matches_membership(c, operator or "in", value) for c in candidates):
                return True, f"Condition: {cond.display or cond.code}"
        return False, None

    # Otherwise treat the condition type as an observation code and compare values
    for obs in pc.observations:
        if str(obs.code).lower() == str(c_type).lower():
            try:
                if _compare_numeric(float(obs.value), operator, float(value)):
                    return True, f"{obs.display or obs.code}: {obs.value} {obs.unit or ''}".strip()
            except (ValueError, TypeError):
                logger.warning("Could not compare observation %s with condition value %s", obs.code, value)
    return False, None

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