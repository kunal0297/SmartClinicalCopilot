# Smart Clinical Copilot 

A fast, personalized, and explainable clinical decision support system (CDSS) built on **InterSystems IRIS for Health Community Edition**. This system integrates **FHIR data ingestion**, **Trie-based rule matching**, and **LLM-powered natural language explanations** to deliver context-aware alerts and evidence-driven clinical reasoning.

---

## 🌟 Key Features

###  FHIR Data Engine
- Real-time integration with **InterSystems IRIS for Health Community Edition**
- Structured ingestion of patient Conditions, Medications, and Lab Results
- Secure IRIS credential-based authentication
- Optimized caching for high-performance querying

###  Trie Rule Matcher
- High-speed rule matching using a Trie data structure
- Support for complex, multi-condition clinical rules
- Real-time rule validation and intelligent suggestions
- Rapid pattern matching for clinical scenarios

###  Alert Generator
- Prioritized clinical alerts based on severity and confidence scores
- Context-sensitive alert generation
- Seamless integration with evidence-based clinical guidelines
- Real-time alert delivery to the user interface

###  LLM Reasoning Module
- AI-generated natural language explanations for clinical alerts
- Contextual evidence summaries and guideline references
- Template-based fallback explanations when LLM API is unavailable

###  Feedback and Learning System
- Clinician feedback collection on alert usefulness
- Rule-specific feedback analytics and usage statistics
- Continuous alerting system improvement via feedback loop
- Historical feedback tracking and reporting

---

##  InterSystems IRIS for Health Integration

This application uses **InterSystems IRIS for Health Community Edition** as its primary FHIR data server and clinical data repository. It leverages native **FHIR R4 Resource Repository** and **FHIR REST APIs** for secure, real-time healthcare data exchange.

---

##  System Architecture Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   FHIR Engine   │────▶│  Trie Matcher   │────▶│ Alert Generator │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  LLM Explainer  │◀───▶│  Feedback Sys   │◀───▶│   Copilot UI    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

##  Getting Started

###  Prerequisites

- **Python 3.9**
- **InterSystems IRIS for Health Community Edition**  
  [Download or pull container](https://evaluation.intersystems.com)
- **Node.js 16+** (for frontend)
- **OpenAI API key** (optional, for enhanced LLM explanations)

>  **Note:** For containerized deployment, consider using:

---

##  Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/kunal0297/SmartClinicalCopilot.git
cd SmartClinicalCopilot
```
2️⃣ Backend Setup (Python + FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
3️⃣ Configure Environment Variables
Create a .env file inside the backend directory:
```bash
FHIR_SERVER_URL=http://localhost:52773/csp/healthshare/fhir/r4
IRIS_USERNAME=your_iris_username
IRIS_PASSWORD=your_iris_password
OPENAI_API_KEY=your_openai_api_key  # optional
```
4️⃣ Start Backend Server
```bash
python app.py
```
5️⃣ Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
 Example Clinical Use Case
Patient: 68 y/o male with CKD Stage 4, prescribed ibuprofen

## Workflow:

System retrieves patient data via FHIR API from IRIS

Trie Matcher identifies NSAID nephrotoxicity rule conflict

Alert Generator flags severity: High

LLM Reasoning Module explains:

"This patient has advanced chronic kidney disease (eGFR < 30) and is prescribed ibuprofen, a nephrotoxic NSAID. According to KDIGO 2021 guidelines, NSAIDs should be avoided in this population due to the risk of renal function deterioration."

System suggests safer alternatives (e.g., acetaminophen) and lab review
---
## Performance Benchmarks
| Task                       | Response Time |
| :------------------------- | :------------ |
| Rule Matching              | < 100 ms      |
| FHIR Data Retrieval        | < 500 ms      |
| LLM Explanation Generation | < 2 sec       |
| End-to-End System Response | < 3 sec       |
---
 ## Security Features
• Secure IRIS credential authentication

• CORS protection for cross-origin requests

• API request input validation

• Rate limiting for API endpoints

• Centralized error handling and logging
---
📡 API Endpoints
| Method | Endpoint              | Description                        |
| :----- | :-------------------- | :--------------------------------- |
| `GET`  | `/patients/{id}`      | Retrieve patient FHIR data         |
| `POST` | `/match-rules`        | Match clinical rules for a patient |
| `POST` | `/suggest-rules`      | Suggest new clinical rules         |
| `POST` | `/feedback`           | Submit alert feedback              |
| `GET`  | `/feedback/{rule_id}` | Retrieve feedback stats by rule    |
| `GET`  | `/feedback/recent`    | View recent feedback entries       |
---
## Contributing
Fork this repository

1. Create your feature branch (git checkout -b feature/foo)

2. Commit your changes (git commit -am 'Add new feature')

3. Push to your branch (git push origin feature/foo)

4. Open a Pull Request
---
## License
This project is licensed under the MIT License — see the LICENSE file for details.
---
## Acknowledgments

InterSystems IRIS for Health

FastAPI

OpenAI

FHIR Community

React & Vite
