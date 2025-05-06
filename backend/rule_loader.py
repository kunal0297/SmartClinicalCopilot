import yaml
import json
import os
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleLoader:
    def __init__(self, rules_path: str = "rules"):
        self.rules_path = rules_path
        self.supported_formats = {".yaml", ".yml", ".json"}

    def load_rules(self) -> List[Dict[str, Any]]:
        """
        Load and parse all rule files (YAML or JSON) from the rules directory.
        Returns a list of rule dictionaries.
        """
        if not os.path.exists(self.rules_path):
            raise FileNotFoundError(f"Rules directory '{self.rules_path}' does not exist.")

        rule_list = []
        for filename in os.listdir(self.rules_path):
            filepath = os.path.join(self.rules_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext not in self.supported_formats:
                logger.warning(f"Skipping unsupported file format: {filename}")
                continue

            try:
                if file_ext in {".yaml", ".yml"}:
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                elif file_ext == ".json":
                    with open(filepath, "r") as f:
                        data = json.load(f)

                if isinstance(data, dict):
                    rules = data.get("rules")
                    if isinstance(rules, list):
                        rule_list.extend(rules)
                elif isinstance(data, list):
                    rule_list.extend(data)
                else:
                    logger.warning(f"Unexpected data format in file: {filename}")
            except Exception as e:
                logger.error(f"Error loading rules from file {filename}: {str(e)}")
                continue

        logger.info(f"Successfully loaded {len(rule_list)} rules")
        return rule_list

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Validate a single rule dictionary.
        """
        required_fields = {"id", "text"}
        if not isinstance(rule, dict) or not required_fields.issubset(rule.keys()):
            return False
        return True

    def filter_valid_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and return only valid rules from the list.
        """
        return [rule for rule in rules if self.validate_rule(rule)]

# Example usage:
# loader = RuleLoader(rules_path="rules")
# raw_rules = loader.load_rules()
# valid_rules = loader.filter_valid_rules(raw_rules)
# print(valid_rules)
