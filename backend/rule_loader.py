import os
import yaml
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Condition(BaseModel):
    type: str
    operator: str
    value: Any
    unit: str = None
    source: str = None

    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['<', '>', '<=', '>=', '=', '==', '!=']
        if v not in valid_operators:
            raise ValueError(f'Invalid operator. Must be one of {valid_operators}')
        return v

class Action(BaseModel):
    type: str
    message: str
    severity: SeverityLevel = SeverityLevel.INFO
    explanation: Dict[str, Any] = None

class Rule(BaseModel):
    id: str
    text: str
    category: str = None
    severity: SeverityLevel = SeverityLevel.INFO
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    conditions: List[Condition]
    actions: List[Action]

class RuleLoader:
    def __init__(self, rules_dir: str = None):
        self.rules_dir = rules_dir or os.path.join(os.path.dirname(__file__), "rules")

    def load_rules(self) -> List[Any]:
        """Load and validate all rules from the rules directory."""
        rules = []
        try:
            for filename in os.listdir(self.rules_dir):
                if filename.endswith(".yaml"):
                    rule_path = os.path.join(self.rules_dir, filename)
                    with open(rule_path, "r") as f:
                        # Load all documents from the YAML file
                        for rule_data in yaml.safe_load_all(f):
                            if rule_data is None:
                                continue
                            try:
                                # Validate rule structure
                                rule = Rule(**rule_data)
                                rules.append(rule)
                                logger.info(f"Successfully loaded rule: {rule.id}")
                            except Exception as e:
                                logger.error(f"Error validating rule in {filename}: {str(e)}")
                                continue
        except Exception as e:
            logger.error(f"Error loading rules: {str(e)}")
            return []
        return rules

    def validate_rule(self, rule_data: Dict[str, Any]) -> bool:
        """Validate a single rule's structure."""
        try:
            Rule(**rule_data)
            return True
        except Exception as e:
            logger.error(f"Error validating rule: {str(e)}")
            return False

    def save_rule(self, rule_data: Dict[str, Any]) -> bool:
        """Save a rule to a YAML file."""
        try:
            # Validate rule structure
            if not self.validate_rule(rule_data):
                return False

            # Create filename from rule ID
            filename = f"{rule_data['id']}.yaml"
            filepath = os.path.join(self.rules_dir, filename)

            # Save rule to file
            with open(filepath, "w") as f:
                yaml.dump(rule_data, f, default_flow_style=False)
            
            logger.info(f"Successfully saved rule: {rule_data['id']}")
            return True
        except Exception as e:
            logger.error(f"Error saving rule: {str(e)}")
            return False

# Example usage:
# rule_loader = RuleLoader()
# rules = rule_loader.load_rules()
# print(rules)
