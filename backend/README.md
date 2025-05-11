# Smart Clinical Copilot - Backend

The backend service for the Smart Clinical Copilot configuration management system. Built with Python, FastAPI, and modern best practices, this service provides a robust and secure API for managing application configurations.

## Features

### Core Features
- RESTful API for configuration management
- Secure storage and encryption
- Configuration validation
- Template management
- Import/Export functionality
- Audit logging
- Performance monitoring

### Advanced Features
- Redis caching
- Prometheus metrics
- Background tasks
- Rate limiting
- Role-based access control
- Database migrations
- API documentation

## Technology Stack

- **Python**: Core programming language
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **Redis**: Caching
- **Prometheus**: Metrics
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **PyJWT**: Authentication
- **Cryptography**: Encryption
- **Pytest**: Testing

## Project Structure

```
backend/
├── alembic/
│   ├── versions/
│   └── env.py
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── templates.py
│   │   │   └── validation.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── config.py
│   │   ├── user.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── config.py
│   │   ├── user.py
│   │   └── audit.py
│   ├── services/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── validation.py
│   └── utils/
│       ├── encryption.py
│       └── validation.py
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
├── main.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Prometheus (optional)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

### Development

1. **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_api/test_config.py
```

2. **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

3. **Code Quality**
```bash
# Linting
flake8

# Type checking
mypy app/

# Formatting
black app/
```

## API Documentation

The API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Core Components

### Configuration Manager
```python
class ConfigManager:
    def __init__(
        self,
        config_dir: str,
        default_format: str = "json",
        reload_interval: int = 300,
        validate_on_load: bool = True,
        encryption_key: Optional[str] = None,
        default_profile: str = "development",
        default_environment: str = "dev"
    ):
        self.config_dir = config_dir
        self.default_format = default_format
        self.reload_interval = reload_interval
        self.validate_on_load = validate_on_load
        self.encryption_key = encryption_key
        self.default_profile = default_profile
        self.default_environment = default_environment
```

### Security Service
```python
class SecurityService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
```

### Validation Service
```python
class ValidationService:
    def __init__(
        self,
        schema_dir: str,
        strict_validation: bool = True
    ):
        self.schema_dir = schema_dir
        self.strict_validation = strict_validation
```

## Database Models

### Configuration
```python
class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    profile = Column(String)
    environment = Column(String)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### User
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Audit Log
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    resource = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## API Endpoints

### Configuration Management
- `GET /api/v1/config`: List configurations
- `POST /api/v1/config`: Create configuration
- `GET /api/v1/config/{key}`: Get configuration
- `PUT /api/v1/config/{key}`: Update configuration
- `DELETE /api/v1/config/{key}`: Delete configuration

### Security
- `POST /api/v1/security/encrypt`: Encrypt value
- `POST /api/v1/security/decrypt`: Decrypt value
- `GET /api/v1/security/keys`: List encryption keys

### Templates
- `GET /api/v1/templates`: List templates
- `POST /api/v1/templates`: Create template
- `GET /api/v1/templates/{id}`: Get template
- `PUT /api/v1/templates/{id}`: Update template
- `DELETE /api/v1/templates/{id}`: Delete template

### Validation
- `POST /api/v1/validation/validate`: Validate configuration
- `GET /api/v1/validation/rules`: List validation rules
- `POST /api/v1/validation/rules`: Create validation rule
- `DELETE /api/v1/validation/rules/{id}`: Delete validation rule

## Performance Optimization

1. **Caching**
   - Redis for configuration caching
   - In-memory caching for frequently accessed data
   - Cache invalidation strategies

2. **Database**
   - Connection pooling
   - Query optimization
   - Indexing strategy

3. **Background Tasks**
   - Async operations
   - Task queue
   - Periodic tasks

## Security

1. **Authentication**
   - JWT-based authentication
   - Password hashing
   - Token refresh

2. **Authorization**
   - Role-based access control
   - Resource-level permissions
   - API key management

3. **Data Protection**
   - Encryption at rest
   - Secure communication
   - Input validation

## Monitoring

1. **Metrics**
   - Prometheus integration
   - Custom metrics
   - Performance monitoring

2. **Logging**
   - Structured logging
   - Log aggregation
   - Error tracking

3. **Health Checks**
   - Service health
   - Dependency health
   - Custom health checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 