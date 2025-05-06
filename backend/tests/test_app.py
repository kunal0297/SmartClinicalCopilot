import pytest
from fastapi.testclient import TestClient
from app import app
from models import Patient, Alert, Rule, SeverityLevel
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def sample_patient():
    return {
        "id": "test_patient_1",
        "name": [{"text": "John Doe"}],
        "gender": "male",
        "birthDate": "1980-01-01",
        "conditions": {
            "observations": [
                {
                    "code": "eGFR",
                    "system": "http://loinc.org",
                    "display": "eGFR",
                    "value": 25.0,
                    "unit": "mL/min/1.73m²",
                    "date": "2024-03-15"
                },
                {
                    "code": "QT_interval",
                    "system": "http://loinc.org",
                    "display": "QT Interval",
                    "value": 480.0,
                    "unit": "ms",
                    "date": "2024-03-15"
                }
            ],
            "medications": [
                {
                    "code": "ibuprofen",
                    "system": "http://snomed.info/sct",
                    "display": "Ibuprofen 400mg",
                    "status": "active",
                    "intent": "order",
                    "date": "2024-03-15"
                },
                {
                    "code": "amiodarone",
                    "system": "http://snomed.info/sct",
                    "display": "Amiodarone 200mg",
                    "status": "active",
                    "intent": "order",
                    "date": "2024-03-15"
                }
            ],
            "conditions": [
                {
                    "code": "CKD_stage_4",
                    "system": "http://snomed.info/sct",
                    "display": "Chronic Kidney Disease Stage 4",
                    "status": "active",
                    "onset": "2023-12-01"
                }
            ]
        }
    }

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Clinical Decision Support System",
        "version": "1.0.0",
        "status": "operational"
    }

def test_match_rules(sample_patient):
    response = client.post("/match-rules", json=sample_patient)
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    
    # Check for CKD NSAID alert
    ckd_alert = next((alert for alert in alerts if alert["rule_id"] == "CKD_NSAID"), None)
    assert ckd_alert is not None
    assert ckd_alert["severity"] == "error"
    assert "eGFR" in ckd_alert["triggered_by"][0]
    assert "Ibuprofen" in ckd_alert["triggered_by"][1]
    
    # Check for QT prolongation alert
    qt_alert = next((alert for alert in alerts if alert["rule_id"] == "QT_Prolongation"), None)
    assert qt_alert is not None
    assert qt_alert["severity"] == "warning"
    assert "QT Interval" in qt_alert["triggered_by"][0]
    assert "Amiodarone" in qt_alert["triggered_by"][1]

def test_explain_rule(sample_patient):
    response = client.post("/explain-rule", params={"rule_id": "CKD_NSAID"}, json=sample_patient)
    assert response.status_code == 200
    explanation = response.json()
    assert "template" in explanation
    assert "variables" in explanation
    assert "guidelines" in explanation

def test_suggest_rules():
    response = client.get("/suggest-rules", params={"prefix": "CKD"})
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert isinstance(suggestions, list)
    assert "CKD_NSAID" in suggestions

def test_invalid_patient_id():
    response = client.get("/patients/invalid_id")
    assert response.status_code == 404

def test_invalid_rule_id():
    response = client.post("/explain-rule", params={"rule_id": "invalid_rule"}, json={})
    assert response.status_code == 404

def test_invalid_patient_data():
    response = client.post("/match-rules", json={})
    assert response.status_code == 422  # Validation error

def test_suggest_rules_empty_prefix():
    response = client.get("/suggest-rules", params={"prefix": ""})
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0 