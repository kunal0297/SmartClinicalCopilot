from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from .database import get_db, engine
from .models import Base
from .schemas import (
    ClinicalRule,
    Alert,
    Patient,
    RuleMatch,
    AlertOverride,
    ClinicalScore
)
from .rules_engine import RulesEngine
from .fhir_client import FHIRClient
from .llm_service import LLMService
from .monitoring import AlertMetrics
from .error_handler import ErrorHandler
from .config import settings
from .logging_config import setup_logging, LogContext

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Clinical Copilot",
    description="AI-powered clinical decision support system",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

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

# Error metrics endpoint
@app.get("/metrics/errors")
async def get_error_metrics():
    with LogContext(endpoint="/metrics/errors"):
        return error_handler.get_error_metrics()

# Initialize services
rules_engine = RulesEngine()
fhir_client = FHIRClient()
llm_service = LLMService()
alert_metrics = AlertMetrics()

@app.get("/")
async def root():
    with LogContext(endpoint="/"):
        return {
            "message": "Welcome to Smart Clinical Copilot API",
            "version": app.version,
            "documentation": "/docs",
            "health": "/health"
        }

@app.post("/rules/evaluate")
async def evaluate_rules(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Evaluate all clinical rules for a patient"""
    with LogContext(
        endpoint="/rules/evaluate",
        patient_id=patient_id
    ):
        try:
            # Get patient data from FHIR
            patient_data = await fhir_client.get_patient_data(patient_id)
            
            # Evaluate rules
            rule_matches = rules_engine.evaluate_all(patient_data)
            
            # Log rule matches
            alert_metrics.log_rule_matches(patient_id, rule_matches)
            
            # Generate explanations using LLM
            explanations = await llm_service.generate_explanations(rule_matches)
            
            return {
                "patient_id": patient_id,
                "rule_matches": rule_matches,
                "explanations": explanations,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error evaluating rules", exc_info=True)
            raise

@app.post("/alerts/override")
async def override_alert(
    alert_id: str,
    override_reason: str,
    db: Session = Depends(get_db)
):
    """Record an alert override"""
    with LogContext(
        endpoint="/alerts/override",
        alert_id=alert_id
    ):
        try:
            override = AlertOverride(
                alert_id=alert_id,
                override_reason=override_reason,
                timestamp=datetime.utcnow()
            )
            db.add(override)
            db.commit()
            
            # Update metrics
            alert_metrics.log_override(alert_id)
            
            return {
                "status": "success",
                "message": "Alert override recorded",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error recording alert override", exc_info=True)
            raise

@app.get("/metrics/alerts")
async def get_alert_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get alert metrics and statistics"""
    with LogContext(
        endpoint="/metrics/alerts",
        start_date=start_date.isoformat() if start_date else None,
        end_date=end_date.isoformat() if end_date else None
    ):
        try:
            metrics = alert_metrics.get_metrics(start_date, end_date)
            return {
                **metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error getting alert metrics", exc_info=True)
            raise

@app.post("/clinical-scores/calculate")
async def calculate_clinical_score(
    score_type: str,
    patient_data: dict,
    db: Session = Depends(get_db)
):
    """Calculate clinical scores (CHA₂DS₂-VASc, Wells, etc.)"""
    with LogContext(
        endpoint="/clinical-scores/calculate",
        score_type=score_type
    ):
        try:
            score = rules_engine.calculate_clinical_score(score_type, patient_data)
            return {
                "score_type": score_type,
                "score": score,
                "interpretation": rules_engine.interpret_score(score_type, score),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error calculating clinical score", exc_info=True)
            raise

@app.get("/smart/launch")
async def smart_launch():
    """SMART on FHIR launch endpoint"""
    with LogContext(endpoint="/smart/launch"):
        try:
            launch_url = fhir_client.get_launch_url()
            return {
                "launch_url": launch_url,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error generating SMART launch URL", exc_info=True)
            raise

# Import and include routers
from .routers import fhir, alerts, rules, users, analytics

app.include_router(fhir.router, prefix="/fhir", tags=["FHIR"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(rules.router, prefix="/rules", tags=["Rules"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG_MODE
    ) 