import pytest
from unittest.mock import patch, AsyncMock
from fhir_client import FHIRClient
from models import Patient, Observation, Medication, Condition

@pytest.fixture
def mock_session():
    with patch('aiohttp.ClientSession') as mock:
        session = AsyncMock()
        mock.return_value.__aenter__.return_value = session
        yield session

@pytest.fixture
def fhir_client(mock_session):
    return FHIRClient()

@pytest.fixture
def sample_fhir_patient():
    return {
        "resourceType": "Patient",
        "id": "test_patient_1",
        "name": [{"text": "John Doe"}],
        "gender": "male",
        "birthDate": "1980-01-01"
    }

@pytest.fixture
def sample_fhir_observations():
    return {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "eGFR",
                            "display": "eGFR"
                        }]
                    },
                    "valueQuantity": {
                        "value": 25.0,
                        "unit": "mL/min/1.73m²"
                    },
                    "effectiveDateTime": "2024-03-15"
                }
            }
        ]
    }

@pytest.fixture
def sample_fhir_medications():
    return {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "medicationCodeableConcept": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "ibuprofen",
                            "display": "Ibuprofen 400mg"
                        }]
                    },
                    "status": "active",
                    "intent": "order",
                    "authoredOn": "2024-03-15"
                }
            }
        ]
    }

@pytest.fixture
def sample_fhir_conditions():
    return {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "CKD_stage_4",
                            "display": "Chronic Kidney Disease Stage 4"
                        }]
                    },
                    "clinicalStatus": {
                        "coding": [{
                            "code": "active"
                        }]
                    },
                    "onsetDateTime": "2023-12-01"
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_get_patient(fhir_client, mock_session, sample_fhir_patient):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_fhir_patient
    )
    
    patient = await fhir_client.get_patient("test_patient_1")
    assert isinstance(patient, Patient)
    assert patient.id == "test_patient_1"
    assert patient.name[0].text == "John Doe"
    assert patient.gender == "male"
    assert patient.birthDate == "1980-01-01"

@pytest.mark.asyncio
async def test_get_patient_not_found(fhir_client, mock_session):
    mock_session.get.return_value.__aenter__.return_value.status = 404
    
    with pytest.raises(Exception) as exc_info:
        await fhir_client.get_patient("nonexistent_patient")
    assert "Patient not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_patient_observations(fhir_client, mock_session, sample_fhir_observations):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_fhir_observations
    )
    
    observations = await fhir_client._fetch_observations("test_patient_1")
    assert len(observations) == 1
    assert observations[0]["code"]["coding"][0]["code"] == "eGFR"
    assert observations[0]["valueQuantity"]["value"] == 25.0

@pytest.mark.asyncio
async def test_get_patient_medications(fhir_client, mock_session, sample_fhir_medications):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_fhir_medications
    )
    
    medications = await fhir_client._fetch_medications("test_patient_1")
    assert len(medications) == 1
    assert medications[0]["medicationCodeableConcept"]["coding"][0]["code"] == "ibuprofen"
    assert medications[0]["status"] == "active"

@pytest.mark.asyncio
async def test_get_patient_conditions(fhir_client, mock_session, sample_fhir_conditions):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_fhir_conditions
    )
    
    conditions = await fhir_client._fetch_conditions("test_patient_1")
    assert len(conditions) == 1
    assert conditions[0]["code"]["coding"][0]["code"] == "CKD_stage_4"
    assert conditions[0]["clinicalStatus"]["coding"][0]["code"] == "active"

@pytest.mark.asyncio
async def test_process_patient_data(fhir_client, sample_fhir_patient, sample_fhir_observations,
                                  sample_fhir_medications, sample_fhir_conditions):
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=[
        sample_fhir_patient,
        sample_fhir_observations,
        sample_fhir_medications,
        sample_fhir_conditions
    ])
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        patient_data = await fhir_client.get_patient("test_patient_1")
        
        assert len(patient_data.conditions.observations) == 1
        assert len(patient_data.conditions.medications) == 1
        assert len(patient_data.conditions.conditions) == 1
        
        observation = patient_data.conditions.observations[0]
        assert isinstance(observation, Observation)
        assert observation.code == "eGFR"
        assert observation.value == 25.0
        
        medication = patient_data.conditions.medications[0]
        assert isinstance(medication, Medication)
        assert medication.code == "ibuprofen"
        assert medication.status == "active"
        
        condition = patient_data.conditions.conditions[0]
        assert isinstance(condition, Condition)
        assert condition.code == "CKD_stage_4"
        assert condition.status == "active"

@pytest.mark.asyncio
async def test_fhir_client_error_handling(fhir_client, mock_session):
    mock_session.get.return_value.__aenter__.return_value.status = 500
    
    with pytest.raises(Exception) as exc_info:
        await fhir_client.get_patient("test_patient_1")
    assert "Error fetching patient" in str(exc_info.value)

@pytest.mark.asyncio
async def test_fhir_client_timeout(fhir_client, mock_session):
    mock_session.get.return_value.__aenter__.side_effect = TimeoutError()
    
    with pytest.raises(Exception) as exc_info:
        await fhir_client.get_patient("test_patient_1")
    assert "Timeout" in str(exc_info.value) 