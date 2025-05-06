# Clinical Rule Schema

## Rule Structure

```yaml
rules:
  - id: "unique_rule_id"
    text: "Human readable rule description"
    category: "medication|lab|condition|procedure"
    severity: "info|warning|error|critical"
    confidence: 0.0-1.0
    conditions:
      - type: "clinical_concept"
        operator: "="|">"|"<"|">="|"<="|"in"|"not_in"
        value: "threshold_or_value"
        unit: "optional_unit"
        source: "FHIR_resource_type"
    actions:
      - type: "alert"
        message: "Alert message"
        severity: "info|warning|error|critical"
      - type: "suggestion"
        message: "Suggested action"
        references:
          - type: "guideline"
            id: "guideline_id"
            text: "Guideline reference"
      - type: "explanation"
        template: "Explanation template with {variables}"
        variables:
          - name: "variable_name"
            source: "condition_or_value"
```

## Example Rules

### Medication Rule
```yaml
rules:
  - id: "CKD_NSAID"
    text: "Avoid NSAIDs in advanced CKD"
    category: "medication"
    severity: "error"
    confidence: 0.95
    conditions:
      - type: "eGFR"
        operator: "<"
        value: 30
        unit: "mL/min/1.73m²"
        source: "Observation"
      - type: "medication"
        operator: "in"
        value: ["ibuprofen", "naproxen", "diclofenac"]
        source: "MedicationRequest"
    actions:
      - type: "alert"
        message: "Patient should avoid NSAIDs due to advanced CKD"
        severity: "error"
      - type: "suggestion"
        message: "Consider acetaminophen or topical NSAIDs for pain management"
        references:
          - type: "guideline"
            id: "KDIGO_2021"
            text: "KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases"
      - type: "explanation"
        template: "This patient has advanced chronic kidney disease (eGFR {eGFR}) and is prescribed {medication}, a nephrotoxic NSAID. According to {guideline}, NSAIDs should be avoided in this population due to the risk of renal function deterioration."
        variables:
          - name: "eGFR"
            source: "condition.eGFR"
          - name: "medication"
            source: "condition.medication"
          - name: "guideline"
            source: "action.references[0].text"
```

### Lab Rule
```yaml
rules:
  - id: "QT_Prolongation"
    text: "Monitor for QT prolongation"
    category: "lab"
    severity: "warning"
    confidence: 0.85
    conditions:
      - type: "QT_interval"
        operator: ">"
        value: 450
        unit: "ms"
        source: "Observation"
      - type: "medication"
        operator: "in"
        value: ["amiodarone", "sotalol", "dofetilide"]
        source: "MedicationRequest"
    actions:
      - type: "alert"
        message: "Patient is at risk for QT prolongation"
        severity: "warning"
      - type: "suggestion"
        message: "Consider ECG monitoring and review medications"
        references:
          - type: "guideline"
            id: "ACC_2020"
            text: "ACC/AHA/HRS 2020 Guidelines for Management of Patients With Ventricular Arrhythmias"
      - type: "explanation"
        template: "Patient has prolonged QT interval ({qt_interval}ms) and is taking {medication}, which can further prolong QT. According to {guideline}, this combination requires careful monitoring."
        variables:
          - name: "qt_interval"
            source: "condition.QT_interval"
          - name: "medication"
            source: "condition.medication"
          - name: "guideline"
            source: "action.references[0].text"
```


