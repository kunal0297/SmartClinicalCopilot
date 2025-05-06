# Rule Definition Schema

## Overview

Each rule is defined in a YAML file and consists of the following components:

### Fields

- **id**: (string) A unique identifier for the rule.
- **text**: (string) A human-readable description of the rule.
- **conditions**: (array) A list of conditions that must be met for the rule to apply.
  - **type**: (string) The type of condition (e.g., eGFR, QT_interval).
  - **operator**: (string) The comparison operator (e.g., <, >, =).
  - **value**: (number) The threshold value for the condition.
- **actions**: (array) A list of actions to take if the rule is triggered.
  - **type**: (string) The type of action (e.g., alert).
  - **message**: (string) The message to display when the action is triggered.

### Example Rule

```yaml
rules:
  - id: "Example_Rule"
    text: "Example rule description."
    conditions:
      - type: "Example_Condition"
        operator: "<"
        value: 100
    actions:
      - type: "alert"
        message: "This is an example alert message."
Notes
Ensure that the id field is unique across all rules.
The conditions and actions fields can contain multiple entries to define complex rules.
The structure should be consistent to allow for easy parsing and processing by the rule engine.


---

### Summary of the `rules` Directory Structure
rules/ ├── CKD_NSAID.yaml # Rule to avoid NSAIDs if eGFR < 30 ├── QT_Prolongation.yaml # Rule regarding risk of QT prolongation └── schema.md # Rule definition schema


### Usage

- Place these files in the `rules` directory of your project.
- The `rule_loader.py` will read these files and extract the rules for insertion into the trie engine.

Feel free to modify the content of the YAML files and the schema as needed to fit your specific clinical rules and requirements!


