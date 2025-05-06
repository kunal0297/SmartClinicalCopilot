# Backend - FHIR Rules & LLM Services

## Overview

This backend provides:

- A FastAPI application (`app.py`) that handles clinical rule matching and explanations.
- A C-based trie engine (via Python wrapper) for efficient rule matching.
- Integration with OpenAI’s GPT models for clinical rule explanation.
- A FHIR client to pull patient data from IRIS.
- Rule loading utilities for ingesting YAML/JSON rule files.

## Setup

1. **Install Dependencies**

   pip install -r requirements.txt
Build C Extension

Assuming the C source files and wrapper are in place:

python setup.py build
python setup.py install
Environment Variables

Set OPENAI_API_KEY to your OpenAI API key.
Configure other necessary environment variables as needed.
Run the FastAPI App


uvicorn app:app --reload --host 0.0.0.0 --port 8000
Usage
Use the /match-rules endpoint to find triggered alerts given a patient.
Use the /explain-rule endpoint to get human-readable explanations.
Use the /patients/{id} endpoint to fetch patient data from IRIS.
Adding Rules
Add your clinical rules as .yaml or .json files under the rules directory.
The rule_loader module will parse and load them into the trie.
Extending
Extend models in models.py to accommodate more FHIR resources or alert types.
Enhance LLM prompt engineering inside llm_explainer.py.
This backend is designed to be modular and efficient for clinical rule-based decision support with AI explanations.

If you want, I can also prepare `setup.py` for building the C extension and other integration configurations. Just ask!
