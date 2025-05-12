# Smart Clinical Copilot - Configuration Management System

**Smart Clinical Copilot** is a next-generation, AI-powered Clinical Decision Support System (CDSS) built to empower healthcare professionals with intelligent, real-time insights derived from complex clinical data. It is purposefully designed to integrate seamlessly into modern healthcare infrastructures, offering an advanced suite of tools to enhance clinical decision-making, reduce alert fatigue, improve patient safety, and support transparent, explainable recommendations. This system is optimized for integration with HL7 FHIR-based Electronic Health Records (EHRs), ensuring interoperability, scalability, and adaptability.

> **Author**: Kunal Pandey  
> **Team Members**: Solo Project  
> **Contest**: InterSystems FHIR and Digital Health Interoperability Contest

---

## 🚀 Key Features

### 🔗 Real-Time FHIR Integration
- Continuous, real-time clinical data retrieval from HL7 FHIR R4 servers using SMART on FHIR or direct API communication.
- Intelligent alert generation based on context-aware analysis of patient vitals, history, lab results, and clinical encounters.

### ⚡ High-Performance Rule Engine
- A custom trie-based engine capable of evaluating thousands of clinical rules within milliseconds.
- Rules defined in YAML format, enabling easy customization, modular design, and support for multi-conditional logic.
- Dynamic rule reloading without restarting services.

### 🤖 AI-Powered Explanations
- Seamless integration with OpenAI GPT-4 to generate clinician-friendly, natural language rationales for triggered alerts.
- Citations and links to guideline sources embedded within explanations to ensure transparency and trust.

### 📚 Guideline-Based Clinical Rules
- Support for a wide range of clinical guidelines:
  - **KDIGO** (Kidney Disease)
  - **ACC/AHA** (Cardiology)
  - **ADA** (Diabetes)
  - **CDC** (Infectious Diseases)
  - **GOLD** (Pulmonary Diseases)
- Custom threshold tuning, localization of rules, and severity grading of alerts.

### 🛠️ Configuration Management Interface
- Web-based UI to define, validate, and deploy clinical rules.
- Rule versioning, import/export capabilities, YAML linting, and real-time updates.
- Monaco-based editor for seamless rule writing and testing.

### 🔄 Self-Healing Framework
- Automated detection and recovery from system-level errors, connection losses, or service crashes.
- Error signature pattern matching and retry logic.
- Metrics and diagnostics exposed via Prometheus endpoints.

### 🔐 Comprehensive Security
- Industry-standard authentication via OAuth2 (SMART on FHIR) and optional API key validation.
- Planned integration of Role-Based Access Control (RBAC).
- Secure storage of credentials, encrypted communication, and audit logging.
- Compliant with HIPAA, GDPR, and other regulatory frameworks.

### 📊 Analytics and Feedback Loop
- Real-time dashboards for rule effectiveness, alert override rates, clinician feedback, and alert fatigue analytics.
- Built-in feedback submission for clinicians to approve, reject, or comment on alerts.
- Longitudinal analysis to refine rule sets over time.

---

## 🧠 System Architecture Overview

### Frontend
- **Framework**: React (Vite-powered) with TypeScript
- **Styling**: Material-UI (MUI)
- **Code Editor**: Monaco Editor for advanced YAML editing
- **Charts**: Recharts for visual data representation
- **UX Design**: Fully responsive for desktops, tablets, and mobile devices

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Cache/State Store**: Redis for high-performance alerting and analytics
- **AI Layer**: OpenAI GPT-4 integration
- **Self-Healing Engine**: YAML-defined recovery rules and diagnostics engine

### Infrastructure
- **FHIR Server**: InterSystems IRIS for Health (or any R4-compliant FHIR server)
- **Deployment**: Docker-based deployment with Compose for local and production environments
- **Monitoring**: Prometheus integration with metrics and alert rule exposure

### Data Flow
1. **Ingestion** – OAuth2 or service-credential-based pull of patient data from FHIR endpoints
2. **Processing** – Rule engine evaluates applicable clinical rules in real time
3. **Alerting** – Alerts generated with severity and guideline metadata
4. **Explanation** – GPT-4 generates clinician-readable narratives and justifications
5. **Feedback** – Clinician input informs analytics and future rule refinement

---

## 🔧 Setup Instructions

### Prerequisites

Make sure you have the following installed on your system:
- **Node.js** (v16+)
- **Python** (3.10.8)
- **Redis** (optional, but recommended)
- **Docker** (optional for containerized deployment)
- **OpenAI API Key** (optional for AI explanations)
- **FHIR Server** (e.g., IRIS for Health)

### 1. Clone the Repository

```bash
git clone https://github.com/kunal0297/SmartClinicalCopilot.git
cd SmartClinicalCopilot
```
2. Backend Setup

Create a virtual environment and activate it:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # For Windows
# OR
source venv/bin/activate  # For Mac/Linux
```
Install Dependencies Manually

Since the requirements.txt file has been removed from the repository, you will need to install the required dependencies manually.

Here are the core dependencies you need to install:
```bash
pip install fastapi==0.95.2
pip install pydantic>=2.5.3,<3.0.0
pip install uvicorn==0.15.0
pip install python-dotenv==1.0.0
pip install python-multipart==0.0.6
pip install httpx
pip install pyyaml==6.0.2
pip install aiohttp==3.11.18
pip install requests==2.31.0
pip install openai==1.3.0
pip install tenacity==8.2.3
pip install shap==0.44.0
pip install scikit-learn==1.4.2
pip install matplotlib==3.8.4
pip install numpy==1.26.4
pip install ollama-python==0.1.1
pip install fhirclient==4.3.1
pip install prometheus-client==0.19.0
pip install prometheus-fastapi-instrumentator==6.1.0
pip install python-json-logger==2.0.7
pip install cryptography==42.0.2
pip install aiofiles==23.2.1
pip install click==8.1.7
pip install rich==13.7.0
pip install tabulate==0.9.0
pip install redis==5.0.1
pip install cachetools==5.3.2
```
After installation, you can proceed to start the backend:
```bash
uvicorn main:app --reload
```
3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Access at: http://localhost:30004.

Environment Configuration
Create .env file in backend/:
```bash
FHIR_SERVER_URL=http://localhost:52773/csp/healthshare/fhir/r4
IRIS_USERNAME=your_iris_username
IRIS_PASSWORD=your_iris_password
SMART_CLIENT_ID=your_smart_client_id
SMART_CLIENT_SECRET=your_smart_client_secret
OPENAI_API_KEY=your_openai_api_key
```
5. Docker Deployment (Optional)
```bash
docker-compose up -d
# To stop:
docker-compose down
```
6. Verify Installation
Test backend:
```bash
curl http://localhost:8000/health
```
Expected response:
```bash
{"status": "ok"}
```
Open the frontend: http://localhost:3000

🤝 Contributions
This is a solo project submitted for the InterSystems Digital Health Contest. Contributions are welcome for future enhancements.

Guidelines
Fork the repository

Submit detailed pull requests with test coverage

Follow PEP8, ESLint, and YAML best practices

Include documentation updates for any new functionality
📄 License
This project is licensed under the MIT License. See the LICENSE file for full details.
