import pytest
import os
import yaml
from rule_loader import RuleLoader
from models import Rule, SeverityLevel

@pytest.fixture
def temp_rules_dir(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    return rules_dir

@pytest.fixture
def sample_rule_file(temp_rules_dir):
    rule_data = {
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
    
    rule_file = temp_rules_dir / "CKD_NSAID.yaml"
    with open(rule_file, "w") as f:
        yaml.dump(rule_data, f)
    
    return rule_file

@pytest.fixture
def invalid_rule_file(temp_rules_dir):
    invalid_data = {
        "id": "Invalid_Rule",
        "text": "Invalid rule without required fields"
    }
    
    rule_file = temp_rules_dir / "Invalid_Rule.yaml"
    with open(rule_file, "w") as f:
        yaml.dump(invalid_data, f)
    
    return rule_file

@pytest.fixture
def rule_loader(temp_rules_dir):
    return RuleLoader(str(temp_rules_dir))

def test_rule_loader_initialization(rule_loader, temp_rules_dir):
    assert rule_loader.rules_dir == str(temp_rules_dir)
    assert isinstance(rule_loader.rules, dict)
    assert len(rule_loader.rules) == 0

def test_load_rules(rule_loader, sample_rule_file):
    rules = rule_loader.load_rules()
    assert len(rules) == 1
    assert "CKD_NSAID" in rules
    assert isinstance(rules["CKD_NSAID"], Rule)
    assert rules["CKD_NSAID"].id == "CKD_NSAID"
    assert rules["CKD_NSAID"].text == "Avoid NSAIDs in advanced CKD"
    assert rules["CKD_NSAID"].severity == SeverityLevel.ERROR
    assert rules["CKD_NSAID"].confidence == 0.95

def test_load_invalid_rule(rule_loader, invalid_rule_file):
    rules = rule_loader.load_rules()
    assert len(rules) == 0

def test_validate_rule(rule_loader, sample_rule_file):
    with open(sample_rule_file) as f:
        rule_data = yaml.safe_load(f)
    
    validated_rule = rule_loader.validate_rule(rule_data)
    assert isinstance(validated_rule, Rule)
    assert validated_rule.id == "CKD_NSAID"
    assert validated_rule.text == "Avoid NSAIDs in advanced CKD"
    assert validated_rule.severity == SeverityLevel.ERROR
    assert validated_rule.confidence == 0.95

def test_validate_invalid_rule(rule_loader):
    invalid_rule = {
        "id": "Invalid_Rule",
        "text": "Invalid rule without required fields"
    }
    
    with pytest.raises(Exception) as exc_info:
        rule_loader.validate_rule(invalid_rule)
    assert "Validation error" in str(exc_info.value)

def test_save_rule(rule_loader, temp_rules_dir):
    rule_data = {
        "id": "New_Rule",
        "text": "New test rule",
        "category": "test",
        "severity": "info",
        "confidence": 0.8,
        "conditions": [],
        "actions": [
            {
                "type": "alert",
                "message": "Test message",
                "severity": "info"
            }
        ]
    }
    
    rule = rule_loader.validate_rule(rule_data)
    rule_loader.save_rule(rule)
    
    # Check if file was created
    rule_file = temp_rules_dir / "New_Rule.yaml"
    assert rule_file.exists()
    
    # Check if rule can be loaded back
    with open(rule_file) as f:
        loaded_data = yaml.safe_load(f)
    assert loaded_data["id"] == "New_Rule"
    assert loaded_data["text"] == "New test rule"

def test_load_rules_with_invalid_yaml(rule_loader, temp_rules_dir):
    # Create a file with invalid YAML
    invalid_file = temp_rules_dir / "invalid.yaml"
    with open(invalid_file, "w") as f:
        f.write("invalid: yaml: content: [")
    
    rules = rule_loader.load_rules()
    assert len(rules) == 0

def test_load_rules_with_missing_directory(rule_loader):
    # Create a new loader with non-existent directory
    loader = RuleLoader("nonexistent_dir")
    rules = loader.load_rules()
    assert len(rules) == 0

def test_load_rules_with_empty_directory(rule_loader, temp_rules_dir):
    rules = rule_loader.load_rules()
    assert len(rules) == 0

def test_validate_rule_with_invalid_severity(rule_loader):
    invalid_rule = {
        "id": "Invalid_Severity",
        "text": "Rule with invalid severity",
        "category": "test",
        "severity": "invalid_severity",
        "confidence": 0.8,
        "conditions": [],
        "actions": [
            {
                "type": "alert",
                "message": "Test message",
                "severity": "info"
            }
        ]
    }
    
    with pytest.raises(Exception) as exc_info:
        rule_loader.validate_rule(invalid_rule)
    assert "Invalid severity level" in str(exc_info.value)

def test_validate_rule_with_invalid_confidence(rule_loader):
    invalid_rule = {
        "id": "Invalid_Confidence",
        "text": "Rule with invalid confidence",
        "category": "test",
        "severity": "info",
        "confidence": 1.5,  # Invalid confidence value
        "conditions": [],
        "actions": [
            {
                "type": "alert",
                "message": "Test message",
                "severity": "info"
            }
        ]
    }
    
    with pytest.raises(Exception) as exc_info:
        rule_loader.validate_rule(invalid_rule)
    assert "Confidence must be between 0 and 1" in str(exc_info.value) 