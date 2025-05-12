
# Smart Clinical Copilot - Configuration Management System

# Smart Clinical Copilot 

A modern, secure, and feature-rich configuration management system designed for healthcare applications. This system provides a comprehensive solution for managing application configurations with advanced features like encryption, validation, templates, and more.


## Features

## The AI-Powered Clinical Wingman You Wish You Had in Med School.

🧠 What’s This About?
Smart Clinical Copilot isn’t just another decision support tool —
it’s a next-generation, explainable, evidence-based Clinical Decision Support System (CDSS) built for speed, precision, and transparency.

This is health tech reimagined — engineered to:

⚡ Integrate with FHIR servers in real-time

⚡ Run blazing-fast, multi-condition clinical rule matches

⚡ Deliver AI-powered, guideline-backed recommendations

⚡ Slash alert fatigue with context-aware, severity-based notifications

⚡ Learn from real clinician feedback to get sharper with every case

It’s what happens when you blend cutting-edge AI, precision medicine, and good design thinking into a single, unstoppable tool.


### Core Features
- **Configuration Editor**: Intuitive interface for managing configuration settings
- **Security**: Built-in encryption and access control mechanisms
- **Templates**: Reusable configuration templates with variable support
- **Validation**: Rule-based configuration validation
- **Import/Export**: Support for importing and exporting configurations
- **History**: Track changes and maintain configuration history
- **Statistics**: Monitor configuration usage and performance

### Advanced Features
- **Encryption**: Secure storage of sensitive configuration values
- **Access Control**: Role-based access control for configurations
- **Validation Rules**: Customizable validation rules for configuration values
- **Templates**: Variable-based templates for quick configuration deployment
- **Backup/Restore**: Automatic backup and restore functionality
- **Audit Logging**: Comprehensive audit trail of configuration changes
- **Performance Monitoring**: Real-time performance metrics and statistics

### Self-Healing System
- Automatic error detection and recovery
- Pattern-based error handling
- Service health monitoring
- Resource usage tracking
- Metrics collection and analysis
- Prometheus integration
- Redis-based metrics storage

## Architecture

The system is built using a modern tech stack:

### Frontend
- React with TypeScript
- Material-UI for the component library
- Monaco Editor for code editing
- Recharts for data visualization


### Backend
- Python with FastAPI
- Redis for caching
- Prometheus for metrics
- SQLAlchemy for database operations

## Getting Started

=======
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

A fast, personalized, and explainable clinical decision support system (CDSS) built on **InterSystems IRIS for Health Community Edition**. This system integrates **FHIR data ingestion**, **Trie-based rule matching**, and **LLM-powered natural language explanations** to deliver context-aware alerts and evidence-driven clinical reasoning.

---
⚙️ Tech Stack

| Frontend     | Backend          | AI/LLM                | Data Layer                |
| :----------- | :--------------- | :-------------------- | :------------------------ |
| React + Vite | FastAPI (Python) | OpenAI API (Optional) | IRIS for Health (FHIR R4) |

---
## How It Works

1️⃣ Pulls real-time patient data via FHIR API
2️⃣ Runs fast, multi-condition checks via a Trie-based Rule Matcher
3️⃣ Generates context-aware alerts with severity grading
4️⃣ Uses LLM reasoning to explain alerts with evidence and alternatives
5️⃣ Enables clinician feedback loops for live system optimization
6️⃣ Learns and improves over time through feedback-driven analytics
---
## Security-First Design
🔒 OAuth2 Authentication (SMART on FHIR Ready)
🔒 CORS + Rate Limiting
🔒 Centralized Error Handling
🔒 Role-based Access Control (Coming Soon)
---

### Prerequisites
- Node.js 16+
- Python 3.8+
- Redis
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-clinical-copilot.git
cd smart-clinical-copilot
```


2. Install frontend dependencies:

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
```
---

##  System Architecture Overview

```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- FHIR Server: http://localhost:8080
- IRIS: http://localhost:52773
```

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
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the development servers:


Frontend:
```bash
cd frontend
npm start
```

Backend:
```bash
cd backend
uvicorn main:app --reload
```

Alert Generator flags severity: High


## Usage

### Configuration Management

1. **Creating a Configuration**
   - Click "New Configuration" in the main interface
   - Fill in the required fields
   - Save the configuration

2. **Using Templates**
   - Access the Templates section
   - Choose a template
   - Fill in the variables
   - Apply the template

3. **Security**
   - Access the Security section
   - Configure encryption settings
   - Manage access control rules

4. **Validation**
   - Set up validation rules
   - Run validation on configurations
   - View validation results

### Best Practices

1. **Security**
   - Always encrypt sensitive values
   - Use strong access control rules
   - Regularly rotate encryption keys
   - Monitor access logs

2. **Performance**
   - Use caching for frequently accessed configurations
   - Implement rate limiting
   - Monitor system metrics
   - Optimize database queries

3. **Maintenance**
   - Regular backups
   - Clean up old configurations
   - Update validation rules
   - Monitor system health

## API Documentation

The API documentation is available at `/docs` when running the backend server. It provides detailed information about all available endpoints, request/response formats, and authentication requirements.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Acknowledgments

- Material-UI for the component library
- Monaco Editor for the code editor
- FastAPI for the backend framework
- Redis for caching
- Prometheus for metrics

## System Architecture

### Backend Components
1. **Error Handler**
   - Pattern-based error recognition
   - Automatic recovery strategies
   - Detailed error logging
   - Metrics collection
   - User-friendly error responses

2. **Recovery Strategies**
   - Service restart
   - Database reconnection
   - Memory cleanup
   - Configuration reload
   - Permission checks
   - Security alerts

3. **Health Monitor**
   - System metrics tracking
   - Service health checks
   - Error rate monitoring
   - Resource usage monitoring
   - Prometheus metrics

4. **Configuration Management**
   - YAML-based configuration
   - Runtime configuration reloading
   - Service-specific settings
   - Resource thresholds
   - Alerting configuration

## Configuration

### Self-Healing Configuration
The system is configured through `config/self_healing_config.yaml`:

```yaml
monitoring:
  system_metrics_interval: 60
  service_health_interval: 30
  error_rates_interval: 60

recovery:
  max_retries: 3
  initial_retry_delay: 1.0
  max_retry_delay: 30.0

resources:
  cpu:
    warning_threshold: 70
    critical_threshold: 85
```

### Error Patterns
Error patterns are defined in `config/error_patterns.yaml`:

```yaml
DatabaseError:
  action: check_services
  severity: high
  description: "Database error"
  auto_fix: true
  retry_count: 3
  retry_delay: 2
  recovery_strategy: "reconnect_db"
```

## API Endpoints

### Health Monitoring
- `GET /health` - Get system health status
- `GET /metrics` - Get error metrics
- `POST /recover/{error_type}` - Trigger manual recovery
- `GET /config` - Get current configuration
- `POST /config/reload` - Reload configuration

## Monitoring

### Prometheus Metrics
- `self_healing_errors_total` - Total errors by type
- `self_healing_recoveries_total` - Recovery attempts
- `self_healing_recovery_duration_seconds` - Recovery time
- `self_healing_system_health` - System health metrics

### Redis Metrics
- Error counts by type
- Recovery success rates
- System health history
- Service status

## Error Recovery

The system implements various recovery strategies:

1. **Service Recovery**
   - Automatic service restart
   - Health check verification
   - Connection pool management

2. **Resource Recovery**
   - Memory cleanup
   - Disk space management
   - Connection pool optimization

3. **Data Recovery**
   - Database reconnection
   - Transaction rollback
   - Data validation

4. **Security Recovery**
   - Permission checks
   - IP blocking
   - Security alerts

## Development

### Project Structure
```
SmartClinicalCopilot/
├── backend/
│   ├── error_handler.py
│   ├── recovery_strategies.py
│   ├── monitoring/
│   │   └── health_monitor.py
│   └── self_healing.py
├── config/
│   ├── error_patterns.yaml
│   └── self_healing_config.yaml
└── frontend/
    └── src/
```

### Adding New Recovery Strategies
1. Add strategy to `RecoveryStrategies` class
2. Update error patterns in `error_patterns.yaml`
3. Configure strategy in `self_healing_config.yaml`


---
✨ Why You’ll Love It
✅ Zero black-box alerts
✅ Transparent, explainable, evidence-backed recommendations
✅ Plug-and-play for FHIR systems
✅ AI-enhanced, clinician-controlled
✅ Future-proof with SMART on FHIR + OAuth2


## Why This Matters
In an era where clinical alert fatigue and black-box AI models threaten patient safety, Smart Clinical Copilot delivers transparent, context-aware, and evidence-based decision support — empowering clinicians with not just recommendations, but the reasoning behind them.

It bridges clinical expertise, AI explainability, and real-time interoperability, aligned with HL7 FHIR standards and modern health IT infrastructure.
This isn’t just a clinical decision support tool.
It’s your clinical copilot in the cockpit — built to help you steer complex cases with speed, precision, and confidence.

