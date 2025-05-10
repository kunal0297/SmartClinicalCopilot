from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Clinical Decision Support System",
    description="A comprehensive clinical decision support system with SMART on FHIR integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rules_engine = RulesEngine()
fhir_client = FHIRClient()
llm_service = LLMService()
alert_metrics = AlertMetrics()

@app.get("/")
async def root():
    return {"message": "Clinical Decision Support System API"}

@app.post("/rules/evaluate")
async def evaluate_rules(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Evaluate all clinical rules for a patient"""
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
            "explanations": explanations
        }
    except Exception as e:
        logger.error(f"Error evaluating rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/override")
async def override_alert(
    alert_id: str,
    override_reason: str,
    db: Session = Depends(get_db)
):
    """Record an alert override"""
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
        
        return {"status": "success", "message": "Alert override recorded"}
    except Exception as e:
        logger.error(f"Error recording alert override: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/alerts")
async def get_alert_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get alert metrics and statistics"""
    try:
        metrics = alert_metrics.get_metrics(start_date, end_date)
        return metrics
    except Exception as e:
        logger.error(f"Error getting alert metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clinical-scores/calculate")
async def calculate_clinical_score(
    score_type: str,
    patient_data: dict,
    db: Session = Depends(get_db)
):
    """Calculate clinical scores (CHA₂DS₂-VASc, Wells, etc.)"""
    try:
        score = rules_engine.calculate_clinical_score(score_type, patient_data)
        return {
            "score_type": score_type,
            "score": score,
            "interpretation": rules_engine.interpret_score(score_type, score)
        }
    except Exception as e:
        logger.error(f"Error calculating clinical score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/smart/launch")
async def smart_launch():
    """SMART on FHIR launch endpoint"""
    try:
        launch_url = fhir_client.get_launch_url()
        return {"launch_url": launch_url}
    except Exception as e:
        logger.error(f"Error generating SMART launch URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 