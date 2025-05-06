import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# API Configuration
API_VERSION = "1.0.0"
API_TITLE = "Clinical Decision Support System"
API_DESCRIPTION = "API for clinical rule matching and explanation services"

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")

# FHIR Configuration
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
FHIR_TIMEOUT = int(os.getenv("FHIR_TIMEOUT", "30"))

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

# Rule Configuration
RULES_DIR = os.getenv("RULES_DIR", "rules")
RULE_LOAD_RETRY_ATTEMPTS = int(os.getenv("RULE_LOAD_RETRY_ATTEMPTS", "3"))
RULE_LOAD_RETRY_DELAY = int(os.getenv("RULE_LOAD_RETRY_DELAY", "1"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security Configuration
API_KEY_HEADER = "X-API-Key"
API_KEY = os.getenv("API_KEY")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # in seconds

# Cache Configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # in seconds
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))

# Validation Configuration
MAX_PATIENT_AGE = int(os.getenv("MAX_PATIENT_AGE", "120"))
MIN_PATIENT_AGE = int(os.getenv("MIN_PATIENT_AGE", "0"))
VALID_GENDERS = ["male", "female", "other", "unknown"]

# Error Messages
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

# Success Messages
SUCCESS_MESSAGES = {
    "patient_retrieved": "Patient retrieved successfully",
    "rules_matched": "Rules matched successfully",
    "rule_explained": "Rule explained successfully",
    "rules_suggested": "Rules suggested successfully",
} 