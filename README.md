# SmartClinicalCopilot 🏥

A fast, personalized, and explainable clinical decision support system that uses FHIR, Trie rule-matching, and LLMs to deliver context-aware alerts and AI-driven reasoning support.

## 🌟 Key Features

### 1. FHIR Data Engine
- Real-time integration with InterSystems IRIS for Health
- Structured data ingestion (conditions, medications, lab results)
- Efficient caching system for improved performance
- Secure authentication with IRIS credentials

### 2. Trie Rule Matcher
- Lightning-fast rule matching using Trie data structure
- Support for complex clinical conditions
- Real-time rule validation and suggestions
- Efficient pattern matching for clinical rules

### 3. Alert Generator
- Prioritized alerts based on severity and confidence
- Context-aware alert generation
- Integration with clinical guidelines
- Real-time alert processing

### 4. LLM Reasoning Module
- Natural language explanations for alerts
- Evidence-based recommendations
- Clinical guideline references
- Fallback to template-based explanations when LLM is unavailable

### 5. Feedback System
- Track alert helpfulness
- Rule-specific feedback statistics
- Continuous improvement through user feedback
- Historical feedback analysis

## 🚀 Getting Started

### Prerequisites
- Python 3.9
- InterSystems IRIS for Health
- Node.js 16+ (for frontend)
- OpenAI API key (optional, for enhanced explanations)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SmartClinicalCopilot.git
cd SmartClinicalCopilot
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory:
```
FHIR_SERVER_URL=http://localhost:52773/csp/healthshare/fhir/r4
IRIS_USERNAME=your_iris_username
IRIS_PASSWORD=your_iris_password
OPENAI_API_KEY=your_openai_api_key
```

4. Start the backend server:
```bash
python app.py
```

5. Set up the frontend:
```bash
cd frontend
npm install
npm run dev
```

## 📊 System Architecture

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

## 🔧 API Endpoints

- `GET /patients/{id}` - Get patient data
- `POST /match-rules` - Match clinical rules
- `POST /suggest-rules` - Get rule suggestions
- `POST /feedback` - Submit alert feedback
- `GET /feedback/{rule_id}` - Get rule feedback stats
- `GET /feedback/recent` - Get recent feedback

## 🎯 Example Use Case

Patient: 68 y/o male with CKD Stage 4, on ibuprofen

1. System detects CKD and NSAID usage
2. Trie matcher identifies relevant rule
3. Alert generated with severity level
4. LLM provides explanation:
   "This patient has advanced chronic kidney disease (eGFR < 30) and is prescribed ibuprofen, a nephrotoxic NSAID. According to KDIGO 2021 guidelines, NSAIDs should be avoided in this population due to the risk of renal function deterioration."
5. System suggests: "Consider acetaminophen or topical NSAIDs for pain management. Review recent labs to reassess renal function trend."

## 📈 Performance Metrics

- Rule matching: < 100ms
- FHIR data retrieval: < 500ms
- LLM explanation generation: < 2s
- Overall system response: < 3s

## 🔐 Security Features

- Secure IRIS authentication
- CORS protection
- Input validation
- Rate limiting
- Error handling

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- InterSystems IRIS for Health
- FastAPI
- OpenAI
- FHIR Community
