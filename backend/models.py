# backend/rule_loader.py

import yaml
import json
from typing import List, Dict, Union
import os

class RuleLoader:
    def __init__(self, rules_path: str = "rules"):
        self.rules_path = rules_path

    def load_rules(self) -> List[str]:
        """
        Load and parse all rule files (YAML or JSON) from the rules directory.
        Returns a list of rule strings ready for trie insertion.
        """
        rule_texts = []

        if not os.path.exists(self.rules_path):
            raise FileNotFoundError(f"Rules directory '{self.rules_path}' does not exist.")

        for filename in os.listdir(self.rules_path):
            filepath = os.path.join(self.rules_path, filename)
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(filepath, "r") as f:
                    rules = yaml.safe_load(f)
                    rule_texts.extend(self._extract_rule_texts(rules))
            elif filename.endswith(".json"):
                with open(filepath, "r") as f:
                    rules = json.load(f)
                    rule_texts.extend(self._extract_rule_texts(rules))
            else:
                # Unsupported file format
                continue
        return rule_texts

    def _extract_rule_texts(self, data: Union[Dict, List]) -> List[str]:
        """
        Extract rule text content from loaded data.
        Adjust this method depending on your rule file structure.
        """
        rules = []
        if isinstance(data, dict):
            # Example: rules under 'rules' key
            rule_entries = data.get("rules", [])
            for entry in rule_entries:
                if isinstance(entry, dict) and "text" in entry:
                    rules.append(entry["text"])
                elif isinstance(entry, str):
                    rules.append(entry)
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and "text" in entry:
                    rules.append(entry["text"])
                elif isinstance(entry, str):
                    rules.append(entry)
        return rules

# Example usage:
# loader = RuleLoader(rules_path="rules")
# rule_texts = loader.load_rules()
