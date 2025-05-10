# Smart Clinical Copilot 


A world-class clinical decision support system that combines evidence-based guidelines, high-performance rule matching, and AI-powered explanations to provide real-time clinical guidance.

## 🌟 Key Features

### 1. Evidence-Based Clinical Rules
- Integration with major clinical guidelines (KDIGO, ACC/AHA, ADA)
- High-impact clinical rules for critical scenarios
- Inline citations and guideline references
- Support for clinical prediction rules (CHA₂DS₂-VASc, Wells Score)

### 2. High-Impact Clinical Rules
- Drug-drug interactions (QT prolongation)
- Medication contraindications by lab values
- Duplicate therapy detection
- Opioid risk assessment
- Clinical prediction rule integration

### 3. Trie Rule Matcher
- High-performance rule matching using Trie data structure
- Support for complex clinical conditions and combinations
- Real-time rule validation and suggestions
- Pattern matching for clinical rules with sub-second response times

### 4. Alert System
- Prioritized alerts based on severity and confidence
- Context-aware alert generation
- Integration with clinical guidelines
- Real-time alert processing and delivery

### 5. LLM Reasoning Module
- Natural language explanations for clinical alerts
- Evidence-based recommendations
- Clinical guideline references
- Fallback to template-based explanations
- Local LLM support via Hugging Face Transformers

### 6. Feedback & Analytics
- Track alert helpfulness
- Rule-specific feedback statistics
- Alert fatigue metrics
- Rule firing frequency analysis
- Override rate tracking

### 7. SMART on FHIR Launch and OAuth2 Support
- EHR integration capabilities
- Secure authentication and authorization
- Prometheus monitoring and metrics
=======
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


### Prerequisites
- **Python 3.9+** (Recommended: 3.9 or 3.10)
- **Node.js 16+**
- **Docker & Docker Compose** (for full stack)
- **OpenAI API key** (optional, for LLM explanations)
- **SMART on FHIR credentials** (for EHR integration)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/SmartClinicalCopilot.git
cd SmartClinicalCopilot
```

### 2. Environment Variables
Create a `.env` file in the `backend/` directory with the following (edit as needed):
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# SMART on FHIR
SMART_CLIENT_ID=your_client_id
SMART_CLIENT_SECRET=your_client_secret
SMART_REDIRECT_URI=http://localhost:8000/smart/callback
SMART_STATE_SECRET=your_state_secret
SMART_JWT_SECRET=your_jwt_secret

# FHIR
FHIR_BASE_URL=http://localhost:8080/fhir
FHIR_TIMEOUT=30

# Other (optional)
API_KEY=your_api_key
LOG_LEVEL=INFO
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
pip install --upgrade pip
pip install -r ../requirements.txt
python setup.py build_ext --inplace  # If using C extensions
python app.py
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

### 5. Docker Compose (Full Stack)
```bash
docker-compose up -d
=======
##  InterSystems IRIS for Health Integration

This application uses **InterSystems IRIS for Health Community Edition** as its primary FHIR data server and clinical data repository. It leverages native **FHIR R4 Resource Repository** and **FHIR REST APIs** for secure, real-time healthcare data exchange.

---

##  System Architecture Overview

```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- FHIR Server: http://localhost:8080
- IRIS: http://localhost:52773

## 🧪 Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd ../frontend
npm test
```


## 🛠️ Troubleshooting
- **Python version**: Use Python 3.9 or 3.10 for best compatibility.
- **Missing dependencies**: Run `pip install -r requirements.txt` from the project root.
- **SMART/FHIR errors**: Ensure all SMART and FHIR env variables are set.
- **LLM explanations not working**: Set your OpenAI API key in `.env`.
- **Rule validation errors**: Check YAML files in `backend/rules/` for required fields (`id`, `text`, `conditions`, `actions`).
- **C extension errors**: Run `python setup.py build_ext --inplace` in `backend/`.
- **Docker issues**: Ensure Docker Desktop is running and ports are not in use.

## ✅ Post-Setup Checklist
- [ ] Backend starts with `python app.py` (no import/module errors)
- [ ] Frontend starts with `npm run dev` (shows UI at http://localhost:3000)
- [ ] API docs available at http://localhost:8000/docs
- [ ] Rule YAML files load without critical errors
- [ ] `.env` file is present in `backend/` and all required keys are set
- [ ] (Optional) LLM explanations work if OpenAI key is set

## 📚 Clinical Guidelines

The system implements rules based on the following guidelines:
- KDIGO 2021 Clinical Practice Guidelines
- ACC/AHA Guidelines
- ADA Standards of Medical Care
- CDC Guidelines
- GOLD Guidelines

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


- HAPI FHIR
- FastAPI
- OpenAI
- React
- FHIR Community
- InterSystems IRIS

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
🤝 Author
Developed by Kunal Pandey
GitHub: kunal0297
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

---
## Why This Matters
In an era where clinical alert fatigue and black-box AI models threaten patient safety, Smart Clinical Copilot delivers transparent, context-aware, and evidence-based decision support — empowering clinicians with not just recommendations, but the reasoning behind them.

It bridges clinical expertise, AI explainability, and real-time interoperability, aligned with HL7 FHIR standards and modern health IT infrastructure.

