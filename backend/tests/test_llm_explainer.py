import pytest
from unittest.mock import patch, AsyncMock
from llm_explainer import LLMExplainer
from models import Patient, RuleExplanation

@pytest.fixture
def llm_explainer():
    return LLMExplainer()

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

@pytest.fixture
def sample_rule():
    return {
        "id": "CKD_NSAID",
        "text": "Avoid NSAIDs in advanced CKD",
        "category": "medication",
        "severity": "error",
        "confidence": 0.95,
        "conditions": [
            {
                "type": "lab",
                "code": "eGFR",
                "operator": "<",
                "value": 30,
                "unit": "mL/min/1.73m²"
            },
            {
                "type": "medication",
                "code": "ibuprofen",
                "operator": "=",
                "value": "active"
            }
        ],
        "actions": [
            {
                "type": "alert",
                "message": "Patient with eGFR < 30 mL/min/1.73m² should avoid NSAIDs",
                "severity": "error",
                "explanation": {
                    "template": "Patient {patient_name} has {condition} with eGFR of {egfr_value} {egfr_unit}. NSAIDs should be avoided in this case due to increased risk of {risk}.",
                    "variables": [
                        {"name": "patient_name", "source": "name[0].text"},
                        {"name": "condition", "source": "conditions.conditions[0].display"},
                        {"name": "egfr_value", "source": "conditions.observations[0].value"},
                        {"name": "egfr_unit", "source": "conditions.observations[0].unit"},
                        {"name": "risk", "value": "acute kidney injury"}
                    ],
                    "guidelines": [
                        "KDIGO 2012 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease",
                        "FDA Drug Safety Communication: NSAIDs and Acute Kidney Injury"
                    ]
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_explain_with_llm(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="Based on the patient's eGFR of 25 mL/min/1.73m² and active use of Ibuprofen, this patient is at high risk for acute kidney injury. NSAIDs should be discontinued and alternative pain management should be considered."
                    )
                )
            ]
        )
        
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert explanation.template == sample_rule["actions"][0]["explanation"]["template"]
        assert len(explanation.variables) == 5
        assert len(explanation.guidelines) == 2

@pytest.mark.asyncio
async def test_explain_with_template(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert explanation.template == sample_rule["actions"][0]["explanation"]["template"]
        assert len(explanation.variables) == 5
        assert len(explanation.guidelines) == 2

@pytest.mark.asyncio
async def test_explain_invalid_rule_id(llm_explainer, sample_patient):
    with pytest.raises(Exception) as exc_info:
        await llm_explainer.explain("invalid_rule", sample_patient)
    assert "Rule not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_explain_missing_patient_data(llm_explainer, sample_rule):
    with pytest.raises(Exception) as exc_info:
        await llm_explainer.explain("CKD_NSAID", {})
    assert "Invalid patient data" in str(exc_info.value)

@pytest.mark.asyncio
async def test_explain_llm_api_error(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert "template" in explanation.dict()
        assert "variables" in explanation.dict()
        assert "guidelines" in explanation.dict()

@pytest.mark.asyncio
async def test_explain_llm_timeout(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create', side_effect=TimeoutError("API Timeout")):
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert "template" in explanation.dict()
        assert "variables" in explanation.dict()
        assert "guidelines" in explanation.dict()

@pytest.mark.asyncio
async def test_explain_llm_rate_limit(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create', side_effect=Exception("Rate limit exceeded")):
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert "template" in explanation.dict()
        assert "variables" in explanation.dict()
        assert "guidelines" in explanation.dict()

@pytest.mark.asyncio
async def test_explain_llm_invalid_response(llm_explainer, sample_patient, sample_rule):
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content=None
                    )
                )
            ]
        )
        explanation = await llm_explainer.explain("CKD_NSAID", sample_patient)
        assert isinstance(explanation, RuleExplanation)
        assert "template" in explanation.dict()
        assert "variables" in explanation.dict()
        assert "guidelines" in explanation.dict() 