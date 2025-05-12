import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import yaml
import threading
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class MockRedis:
    """In-memory Redis mock for development"""
    def __init__(self):
        self._data = {}
        self._expiry = {}
        self._lock = threading.Lock()
        
    def ping(self):
        return True
        
    def get(self, key):
        with self._lock:
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._data[key]
                del self._expiry[key]
                return None
            return self._data.get(key)
            
    def set(self, key, value):
        with self._lock:
            self._data[key] = value
            
    def setex(self, key, ttl, value):
        with self._lock:
            self._data[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            
    def delete(self, key):
        with self._lock:
            if key in self._data:
                del self._data[key]
            if key in self._expiry:
                del self._expiry[key]
                
    def hmset(self, key, mapping):
        with self._lock:
            if key not in self._data:
                self._data[key] = {}
            self._data[key].update(mapping)
            
    def hgetall(self, key):
        with self._lock:
            return self._data.get(key, {})
            
    def ttl(self, key):
        with self._lock:
            if key in self._expiry:
                return int((self._expiry[key] - datetime.now()).total_seconds())
            return -1

class Settings:
    API_VERSION = "1.0.0"
    API_TITLE = "Clinical Decision Support System"
    API_DESCRIPTION = "API for clinical rule matching and explanation services"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")
    FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
    FHIR_TIMEOUT = int(os.getenv("FHIR_TIMEOUT", "30"))
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    # Local LLM Configuration
    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "1000"))
    
    # Other Settings
    RULES_DIR = os.getenv("RULES_DIR", "rules")
    RULE_LOAD_RETRY_ATTEMPTS = int(os.getenv("RULE_LOAD_RETRY_ATTEMPTS", "3"))
    RULE_LOAD_RETRY_DELAY = int(os.getenv("RULE_LOAD_RETRY_DELAY", "1"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    API_KEY_HEADER = "X-API-Key"
    API_KEY = os.getenv("API_KEY")
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    MAX_PATIENT_AGE = int(os.getenv("MAX_PATIENT_AGE", "120"))
    MIN_PATIENT_AGE = int(os.getenv("MIN_PATIENT_AGE", "0"))
    VALID_GENDERS = ["male", "female", "other", "unknown"]
    ERROR_MESSAGES = {
        "patient_not_found": "Patient not found",
        "invalid_patient_id": "Invalid patient ID",
        "invalid_rule_id": "Invalid rule ID",
        "rule_not_found": "Rule not found",
        "invalid_request": "Invalid request",
        "server_error": "Internal server error",
        "rate_limit_exceeded": "Rate limit exceeded",
        "unauthorized": "Unauthorized access",
        "forbidden": "Forbidden access",
        "validation_error": "Validation error",
    }
    SUCCESS_MESSAGES = {
        "patient_retrieved": "Patient retrieved successfully",
        "rules_matched": "Rules matched successfully",
        "rule_explained": "Rule explained successfully",
        "rules_suggested": "Rules suggested successfully",
    }
    SMART_CLIENT_ID = os.getenv("SMART_CLIENT_ID")
    SMART_CLIENT_SECRET = os.getenv("SMART_CLIENT_SECRET")
    SMART_REDIRECT_URI = os.getenv("SMART_REDIRECT_URI")
    SMART_STATE_SECRET = os.getenv("SMART_STATE_SECRET")
    SMART_JWT_SECRET = os.getenv("SMART_JWT_SECRET")

    def __init__(self):
        # Load configuration
        self.config = self._load_config()
        
        # Redis settings
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.REDIS_DB = int(os.getenv("REDIS_DB", 0))
        
        # Security settings
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Monitoring settings
        self.METRICS_RETENTION_DAYS = 7
        self.HEALTH_CHECK_INTERVAL = 30
        self.ERROR_RATE_INTERVAL = 60
        
        # Recovery settings
        self.MAX_RETRIES = 3
        self.INITIAL_RETRY_DELAY = 1
        self.MAX_RETRY_DELAY = 30
        
        # Load settings from config
        self._load_from_config()
        
        # Use mock Redis for development
        self.redis_client = MockRedis()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open("config/self_healing_config.yaml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
            
    def _load_from_config(self):
        """Load settings from configuration"""
        try:
            # Monitoring settings
            monitoring = self.config.get("monitoring", {})
            self.METRICS_RETENTION_DAYS = monitoring.get("retention_days", 7)
            self.HEALTH_CHECK_INTERVAL = monitoring.get("service_health_interval", 30)
            self.ERROR_RATE_INTERVAL = monitoring.get("error_rate_interval", 60)
            
            # Recovery settings
            recovery = self.config.get("recovery", {})
            self.MAX_RETRIES = recovery.get("max_retries", 3)
            self.INITIAL_RETRY_DELAY = recovery.get("initial_retry_delay", 1)
            self.MAX_RETRY_DELAY = recovery.get("max_retry_delay", 30)
            
            # Redis settings
            metrics = self.config.get("metrics", {}).get("redis", {})
            self.REDIS_HOST = metrics.get("host", "localhost")
            self.REDIS_PORT = metrics.get("port", 6379)
            self.REDIS_DB = metrics.get("db", 0)
            
        except Exception as e:
            print(f"Error loading settings from config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return getattr(self, key, default)
        
    def set(self, key: str, value: Any):
        """Set setting value"""
        setattr(self, key, value)
        
    def reload(self):
        """Reload settings from configuration"""
        self.config = self._load_config()
        self._load_from_config()

settings = Settings() 