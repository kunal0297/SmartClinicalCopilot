# SmartClinicalCopilot Backend 🚀

The backend service for SmartClinicalCopilot, providing FHIR integration, rule matching, and LLM-powered explanations.

## 🏗️ Architecture

### Core Components

1. **FHIR Client (`fhir_client.py`)**
   - Asynchronous FHIR data retrieval
   - Caching system with TTL
   - Error handling and retries
   - Data normalization

2. **Trie Engine (`trie_engine.py`)**
   - Fast rule matching using Trie data structure
   - Support for complex conditions
   - Real-time rule validation
   - Pattern matching optimization

3. **LLM Explainer (`llm_explainer.py`)**
   - OpenAI GPT-4 integration
   - Template-based fallback system
   - Evidence-based explanations
   - Clinical guideline references

4. **Feedback System (`feedback.py`)**
   - JSON-based feedback storage
   - Rule-specific statistics
   - Historical feedback analysis
   - Performance metrics

### API Endpoints

```python
# Patient Data
GET /patients/{id}              # Get patient data
POST /match-rules              # Match clinical rules
POST /suggest-rules            # Get rule suggestions

# Feedback
POST /feedback                 # Submit alert feedback
GET /feedback/{rule_id}        # Get rule feedback stats
GET /feedback/recent           # Get recent feedback

# System
GET /health                    # Health check
GET /health/detailed          # Detailed health status
GET /metrics                   # Prometheus metrics
```

## 🛠️ Technical Stack

- **Framework**: FastAPI
- **Database**: InterSystems IRIS for Health
- **AI/ML**: OpenAI GPT-4
- **Monitoring**: Prometheus
- **Caching**: TTLCache
- **Authentication**: Basic Auth

## 📦 Dependencies

```txt
fastapi==0.68.0
uvicorn==0.15.0
pydantic==1.8.2
python-dotenv==0.19.0
aiohttp==3.8.1
fhirclient==3.2.0
openai==0.27.0
prometheus-client==0.11.0
cachetools==4.2.4
tenacity==8.0.1
```

## 🔧 Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
# .env
FHIR_SERVER_URL=http://localhost:52773/csp/healthshare/fhir/r4
IRIS_USERNAME=your_username
IRIS_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

4. Start server:
```bash
python app.py
```

## 📊 Performance Optimization

1. **Caching Strategy**
   - Patient data: 5-minute TTL
   - Rule cache: In-memory
   - LLM responses: Template-based fallback

2. **Concurrency**
   - Async/await for I/O operations
   - Connection pooling
   - Rate limiting

3. **Error Handling**
   - Retry mechanism
   - Circuit breaker pattern
   - Graceful degradation

## 🔍 Monitoring

- Prometheus metrics
- Health check endpoints
- Detailed logging
- Performance tracking

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_fhir_client.py
```

## 📈 Performance Metrics

- Rule matching: < 100ms
- FHIR data retrieval: < 500ms
- LLM explanation: < 2s
- Overall response: < 3s

## 🔐 Security

- IRIS authentication
- CORS protection
- Input validation
- Rate limiting
- Error handling

## 🐛 Troubleshooting

1. **Connection Issues**
   - Check IRIS server status
   - Verify credentials
   - Check network connectivity

2. **Performance Issues**
   - Monitor cache hit rates
   - Check response times
   - Review error logs

3. **LLM Issues**
   - Verify API key
   - Check rate limits
   - Review prompt templates

## 📝 License

This project is licensed under the MIT License.
