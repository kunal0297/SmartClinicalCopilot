from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import os
import logging

from backend.database import get_db
from backend.schemas import Patient, Condition, Observation
from backend.fhir_client import FHIRClient
from backend.logging_config import LogContext
from dateutil.parser import parse as parse_date

logger = logging.getLogger(__name__)

router = APIRouter()

DEMO_PATIENTS_FILE = os.path.join(os.path.dirname(__file__), "..", "demo_patients.json")

def load_demo_patients():
    """Load demo patients from JSON file."""
    if not os.path.exists(DEMO_PATIENTS_FILE):
        return []
    with open(DEMO_PATIENTS_FILE, "r") as f:
        return json.load(f)

def save_demo_patients(patients):
    """Save demo patients to JSON file."""
    with open(DEMO_PATIENTS_FILE, "w") as f:
        json.dump(patients, f, indent=2)

@router.get("/demo-patients", response_model=List[Patient])
async def list_demo_patients():
    """List all demo patients."""
    with LogContext(endpoint="/demo-patients", method="GET"):
        try:
            return load_demo_patients()
        except Exception as e:
            logger.error("Error listing demo patients", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to load demo patients")

@router.post("/demo-patients", response_model=Patient)
async def create_demo_patient(patient: Patient):
    """Create a new demo patient."""
    with LogContext(endpoint="/demo-patients", method="POST", patient_id=patient.id):
        try:
            demo_patients = load_demo_patients()
            if any(p.id == patient.id for p in demo_patients):
                raise HTTPException(status_code=400, detail="Patient with this ID already exists")
            demo_patients.append(patient.model_dump())
            save_demo_patients(demo_patients)
            return patient
        except Exception as e:
            logger.error("Error creating demo patient", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create demo patient")

@router.put("/demo-patients/{patient_id}", response_model=Patient)
async def update_demo_patient(patient_id: str, patient: Patient):
    """Update an existing demo patient."""
    with LogContext(endpoint="/demo-patients/{patient_id}", method="PUT", patient_id=patient_id):
        try:
            demo_patients = load_demo_patients()
            for i, p in enumerate(demo_patients):
                if p["id"] == patient_id:
                    demo_patients[i] = patient.model_dump()
                    save_demo_patients(demo_patients)
                    return patient
            raise HTTPException(status_code=404, detail="Demo patient not found")
        except Exception as e:
            logger.error(f"Error updating demo patient {patient_id}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update demo patient")

@router.delete("/demo-patients/{patient_id}")
async def delete_demo_patient(patient_id: str):
    """Delete a demo patient."""
    with LogContext(endpoint="/demo-patients/{patient_id}", method="DELETE", patient_id=patient_id):
        try:
            demo_patients = load_demo_patients()
            initial_count = len(demo_patients)
            demo_patients = [p for p in demo_patients if p["id"] != patient_id]
            if len(demo_patients) == initial_count:
                raise HTTPException(status_code=404, detail="Demo patient not found")
            save_demo_patients(demo_patients)
            return {"status": "deleted", "patient_id": patient_id}
        except Exception as e:
            logger.error(f"Error deleting demo patient {patient_id}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to delete demo patient")

# Assuming FHIRClient is needed for real patient data endpoints
fhir_client = FHIRClient() # You might want to handle this dependency injection properly

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient data by ID (from demo or real FHIR source)."""
    with LogContext(endpoint="/patients/{patient_id}", method="GET", patient_id=patient_id):
        try:
            # Serve demo patient if id starts with 'demo-'
            if patient_id.startswith("demo-"):
                demo_patients = load_demo_patients()
                patient_data = next((p for p in demo_patients if p["id"] == patient_id), None)
                if not patient_data:
                    raise HTTPException(status_code=404, detail="Demo patient not found")
                
                # Convert dict to Patient schema
                return Patient(
                    id=patient_data["id"],
                    name=patient_data.get("name", []), # Ensure name is a list of dicts
                    gender=patient_data.get("gender"),
                    birthDate=parse_date(patient_data.get("birthDate")) if patient_data.get("birthDate") else None,
                    conditions=PatientConditions(
                         medications=[
                             # Convert dict to Medication schema if needed
                             # Assuming Medication schema matches the structure in demo_patients.json
                             # For now, just pass the dicts - adjust if schemas are stricter
                            m for m in patient_data.get("conditions", {}).get("medications", [])
                         ],
                         observations=[
                            # Convert dict to Observation schema if needed
                            # Assuming Observation schema matches the structure in demo_patients.json
                            o for o in patient_data.get("conditions", {}).get("observations", [])
                         ],
                         conditions=[
                             # Convert dict to Condition schema if needed
                             # Assuming Condition schema matches the structure in demo_patients.json
                             c for c in patient_data.get("conditions", {}).get("conditions", [])
                         ],
                    )
                )

            # Get real patient data from FHIR
            patient_data = await fhir_client.get_patient_data(patient_id)
            if not patient_data:
                 # Fallback: try demo patient if real not found
                demo_patients = load_demo_patients()
                patient_data = next((p for p in demo_patients if p["id"] == patient_id), None)
                if not patient_data:
                    raise HTTPException(status_code=404, detail="Patient not found")
                
                 # Convert dict to Patient schema for demo fallback
                return Patient(
                    id=patient_data["id"],
                    name=patient_data.get("name", []), # Ensure name is a list of dicts
                    gender=patient_data.get("gender"),
                    birthDate=parse_date(patient_data.get("birthDate")) if patient_data.get("birthDate") else None,
                    conditions=PatientConditions(
                         medications=[
                            m for m in patient_data.get("conditions", {}).get("medications", [])
                         ],
                         observations=[
                            o for o in patient_data.get("conditions", {}).get("observations", [])
                         ],
                         conditions=[
                             c for c in patient_data.get("conditions", {}).get("conditions", [])
                         ],
                    )
                )

            # Convert FHIR data to our Patient model
            # Assuming fhir_client.get_patient_data returns data already structured for Patient schema
            return Patient(**patient_data)

        except HTTPException as e:
            raise e # Re-raise HTTPExceptions directly
        except Exception as e:
            logger.error(f"Error getting patient data for {patient_id}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve patient data: {str(e)}")

@router.get("/cohort-analytics")
async def cohort_analytics():
    """Return basic cohort analytics (e.g., count of diabetics, hypertensives, etc.)."""
    with LogContext(endpoint="/cohort-analytics", method="GET"):
        try:
            # Example: count patients with diabetes and hypertension
            # This example uses fhir_client, ensure it's properly initialized/available
            # You might need to adapt this based on your actual data source (FHIR or demo)
            
            # For demo patients, you'd iterate through the loaded data:
            demo_patients = load_demo_patients()
            diabetics_count = sum(
                any("Diabetes" in cond.get("code", "") for cond in p.get("conditions", {}).get("conditions", []))
                for p in demo_patients
            )
            hypertensives_count = sum(
                 any("Hypertension" in cond.get("code", "") for cond in p.get("conditions", {}).get("conditions", []))
                 for p in demo_patients
             )

            # If using FHIRClient, uncomment and adapt:
            # diabetics = await fhir_client.search_resources("Condition", params={"code": "E11"})
            # hypertensives = await fhir_client.search_resources("Condition", params={"code": "I10"})
            # return {
            #     "diabetics_count": len(diabetics),
            #     "hypertensives_count": len(hypertensives)
            # }
            
            return {
                "diabetics_count": diabetics_count,
                "hypertensives_count": hypertensives_count
            }
        except Exception as e:
            logger.error("Error in cohort_analytics", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve cohort analytics: {str(e)}") 