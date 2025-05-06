from typing import Dict, Any

SAMPLE_PATIENT: Dict[str, Any] = {
    "id": "example_patient_id",
    "name": [{"text": "John Doe"}],
    "gender": "male",
    "birthDate": "1980-01-01",
    "conditions": {
        "observations": [
            {
                "code": "eGFR",
                "system": "http://loinc.org",
                "display": "eGFR",
                "value": 25,
                "unit": "mL/min/1.73m²",
                "date": "2024-03-15"
            },
            {
                "code": "QT_interval",
                "system": "http://loinc.org",
                "display": "QT Interval",
                "value": 480,
                "unit": "ms",
                "date": "2024-03-15"
            }
        ],
        "medications": [
            {
                "code": "NSAID",
                "system": "http://snomed.info/sct",
                "display": "Ibuprofen 400mg",
                "status": "active",
                "intent": "order",
                "date": "2024-03-10"
            },
            {
                "code": "QT_prolonging",
                "system": "http://snomed.info/sct",
                "display": "Amiodarone 200mg",
                "status": "active",
                "intent": "order",
                "date": "2024-03-01"
            }
        ],
        "conditions": [
            {
                "code": "CKD",
                "system": "http://snomed.info/sct",
                "display": "Chronic Kidney Disease Stage 4",
                "status": "active",
                "onset": "2023-12-01"
            }
        ]
    }
}

def get_sample_patient() -> Dict[str, Any]:
    """Get the sample patient data."""
    return SAMPLE_PATIENT 