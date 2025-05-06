import yaml
import json
from typing import List, Dict, Any
import os

class RuleLoader:
    def __init__(self, rules_path: str = "rules"):
        self.rules_path = rules_path

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
            try:
                if filename.endswith((".yaml", ".yml")):
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                elif filename.endswith(".json"):
                    with open(filepath, "r") as f:
                        data = json.load(f)
                else:
                    # Unsupported file format
                    continue

                # Extract rules from data
                if isinstance(data, dict):
                    rules = data.get("rules")
                    if isinstance(rules, list):
                        rule_list.extend(rules)
                elif isinstance(data, list):
                    rule_list.extend(data)
            except Exception:
                # Skip file if an error occurs
                continue

        return rule_list

# Example usage:
# loader = RuleLoader(rules_path="rules")
# rules = loader.load_rules()
