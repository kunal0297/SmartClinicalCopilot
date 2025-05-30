import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import yaml
import threading
from datetime import datetime, timedelta
from pydantic_settings import BaseSettings
from pydantic import Field

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
            
    def hincrby(self, name, key, amount=1):
        """Increment the value of a hash field by the given amount"""
        with self._lock:
            if name not in self._data:
                self._data[name] = {}
            if key not in self._data[name]:
                self._data[name][key] = 0
            self._data[name][key] = int(self._data[name][key]) + amount
            return self._data[name][key]

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Clinical Copilot"
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "kunalpandey0297@gmail.com")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # FHIR Server
    FHIR_SERVER_URL: str = os.getenv("FHIR_SERVER_URL", "http://localhost:8080/fhir")
    
    # LLM Settings
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    METRICS_RETENTION_DAYS: int = 7
    HEALTH_CHECK_INTERVAL: int = 30
    ERROR_RATE_INTERVAL: int = 60
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Recovery settings
    MAX_RETRIES: int = 3
    INITIAL_RETRY_DELAY: int = 1
    MAX_RETRY_DELAY: int = 30
    
    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # SMART on FHIR settings
    SMART_CLIENT_ID: str = os.getenv("SMART_CLIENT_ID", "smart_clinical_copilot")
    SMART_CLIENT_SECRET: str = os.getenv("SMART_CLIENT_SECRET", "your-smart-client-secret")
    SMART_REDIRECT_URI: str = os.getenv("SMART_REDIRECT_URI", "http://localhost:8000/smart/callback")
    SMART_STATE_SECRET: str = os.getenv("SMART_STATE_SECRET", "your-smart-state-secret")
    SMART_JWT_SECRET: str = os.getenv("SMART_JWT_SECRET", "your-smart-jwt-secret")
    
    # Redis client (not loaded from env)
    redis_client: Optional[MockRedis] = Field(default=None, exclude=True)
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use mock Redis for development
        self.redis_client = MockRedis()
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return getattr(self, key, default)
        
    def set(self, key: str, value: Any):
        """Set setting value"""
        setattr(self, key, value)

# Create settings instance
settings = Settings() 