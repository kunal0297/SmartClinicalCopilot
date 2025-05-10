# SmartClinicalCopilot 🏥

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

## 🚀 Getting Started

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

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- HAPI FHIR
- FastAPI
- OpenAI
- React
- FHIR Community
- InterSystems IRIS
