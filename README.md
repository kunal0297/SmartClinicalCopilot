# Smart Clinical Copilot

Smart Clinical Copilot is a next-generation, AI-powered Clinical Decision Support System (CDSS) designed to revolutionize patient care by transforming clinical data into actionable insights. Built for healthcare IT teams, clinicians, and researchers, it seamlessly integrates with FHIR-based EHR servers, leveraging real-time data and cutting-edge machine learning to provide context-aware, evidence-backed alerts and recommendations. This system is engineered to tackle the most pressing challenges in modern healthcare, including alert fatigue, patient safety, and clinical decision transparency, while providing a robust, scalable foundation for advanced medical applications.

## 🚀 Key Features

* **Real-Time FHIR Integration**

  * Continuous, real-time data retrieval from HL7 FHIR R4 servers using SMART on FHIR protocols or direct API access.
  * Context-aware alerts based on patient data, medical history, and clinical conditions.

* **High-Performance Rule Engine**

  * Fast, trie-based rule engine capable of evaluating complex clinical rules in real-time.
  * Rules defined in YAML for easy customization, supporting multi-condition matching and flexible logic.

* **AI-Powered Explanations**

  * Integrates with OpenAI GPT-4 for generating natural language explanations.
  * Provides guideline-referenced rationales to enhance clinical decision-making and reduce cognitive load for clinicians.

* **Guideline-Based Alerts**

  * Supports major clinical guidelines (e.g., KDIGO, ACC/AHA, ADA, CDC, GOLD) with severity-graded alerts.
  * Customizable rule definitions and threshold tuning for local practices, ensuring clinical relevance.

* **Configuration Management Interface**

  * Web-based UI for defining, testing, and managing clinical rules.
  * Version control, import/export features, validation tools, and real-time rule updates without system restarts.

* **Self-Healing Framework**

  * Automated service recovery for improved reliability and uptime.
  * Real-time monitoring with Prometheus and log-based diagnostics for proactive issue resolution.

* **Comprehensive Security**

  * OAuth2 (SMART on FHIR), API keys, RBAC (planned), and encrypted storage for sensitive data.
  * Full audit trails and compliance with healthcare data protection regulations (e.g., HIPAA, GDPR).

* **Analytics & Feedback Loop**

  * Tracks alert frequency, clinician feedback, and rule effectiveness to optimize performance over time.
  * Includes dashboards for rule performance, alert override rates, and real-time usage statistics.

## 🏗️ Architecture Overview

Smart Clinical Copilot utilizes a modern, containerized microservices architecture that ensures scalability, flexibility, and high availability.

### Frontend

* **Framework**: React + TypeScript (Vite-powered)
* **Styling**: Material-UI, Monaco Editor for YAML rules
* **Visualizations**: Recharts for data analytics and performance monitoring
* **Responsive Design**: Mobile-friendly interfaces for seamless clinician experiences across devices

### Backend

* **Framework**: FastAPI (Python)
* **Data Layer**: SQLAlchemy, Redis for caching and counters
* **AI Integration**: OpenAI API for real-time explanations
* **Self-Healing**: Custom recovery strategies and error pattern matching for robust reliability

### Data Layer

* **FHIR Server**: InterSystems IRIS for Health or any FHIR R4-compliant server
* **Caching and State**: Redis for real-time state management and low-latency response times

### Self-Healing and Monitoring

* **Metrics**: Prometheus for performance metrics and real-time alerting
* **Error Recovery**: YAML-driven recovery rules for rapid incident response and automated issue mitigation

### Data Flow

1. **Data Ingestion** – Periodic data pulls from FHIR server using OAuth or system credentials.
2. **Rule Evaluation** – Real-time rule matching against patient data to trigger meaningful alerts.
3. **Alert Generation** – Severity-graded alerts with guideline references for precise, actionable insights.
4. **AI Explanations** – Optional OpenAI-powered narratives for clinical context, reducing cognitive load.
5. **Feedback Loop** – Continuous improvement based on clinician inputs, ensuring alerts remain relevant and impactful.

## 🔧 Step-by-Step Setup Guide

### Prerequisites

* **Node.js** (v16+ for the frontend)
* **Python** (3.8+ for the backend, 3.9 or 3.10 recommended)
* **Redis** (optional, for caching and metrics)
* **Docker** (optional, for containerized deployment)
* **FHIR Server** (e.g., InterSystems IRIS for Health)
* **OpenAI API Key** (optional, for AI-generated explanations)

### 1. Clone the Repository

```bash
git clone https://github.com/kunal0297/SmartClinicalCopilot.git
cd SmartClinicalCopilot
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows use `venv\Scripts\activate`
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

(Optional) Rebuild C extensions if needed:

```bash
python setup.py build_ext --inplace
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend should now be running at **[http://localhost:8000](http://localhost:8000)**.

### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the frontend development server:

```bash
npm run dev
```

The frontend should now be running at **[http://localhost:3000](http://localhost:3000)**.

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory with the following:

```ini
FHIR_SERVER_URL=http://localhost:52773/csp/healthshare/fhir/r4
IRIS_USERNAME=your_iris_username
IRIS_PASSWORD=your_iris_password
SMART_CLIENT_ID=your_smart_client_id
SMART_CLIENT_SECRET=your_smart_client_secret
OPENAI_API_KEY=your_openai_api_key
```

### 5. Docker Deployment (Optional)

For an all-in-one deployment:

```bash
docker-compose up -d
```

Stop and clean up:

```bash
docker-compose down
```

### 6. Verify Installation

Test the backend:

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "ok"}`.

Test the frontend by opening **[http://localhost:3000](http://localhost:3000)** in your browser.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

* Fork the repository.
* Write tests for any new functionality.
* Follow coding standards (PEP8, ESLint, YAML best practices).
* Update documentation as needed.

## 📄 License

MIT License. See LICENSE file for details.
