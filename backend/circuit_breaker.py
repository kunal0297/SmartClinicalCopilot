import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
from .config import settings

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialize circuit breaker metrics"""
        metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "successful_requests": 0,
            "circuit_opens": 0,
            "circuit_closes": 0,
            "half_open_attempts": 0
        }
        self.redis_client.hmset("circuit_breaker_metrics", metrics)
        
    def allow_request(self, operation: str) -> bool:
        """Check if request should be allowed based on circuit state"""
        try:
            # Get circuit state
            state = self._get_circuit_state(operation)
            
            if state == "open":
                # Check if circuit should be half-open
                if self._should_allow_half_open(operation):
                    self._set_circuit_state(operation, "half-open")
                    return True
                return False
                
            elif state == "half-open":
                # Allow limited requests in half-open state
                if self._should_allow_half_open_request(operation):
                    return True
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking circuit state for {operation}", exc_info=True)
            return False
            
    def record_success(self, operation: str):
        """Record successful operation"""
        try:
            # Update metrics
            self.redis_client.hincrby("circuit_breaker_metrics", "total_requests", 1)
            self.redis_client.hincrby("circuit_breaker_metrics", "successful_requests", 1)
            
            # Reset failure count
            self.redis_client.delete(f"circuit_breaker:failures:{operation}")
            
            # Close circuit if half-open
            if self._get_circuit_state(operation) == "half-open":
                self._set_circuit_state(operation, "closed")
                self.redis_client.hincrby("circuit_breaker_metrics", "circuit_closes", 1)
                
        except Exception as e:
            logger.error(f"Error recording success for {operation}", exc_info=True)
            
    def record_failure(self, operation: str):
        """Record failed operation"""
        try:
            # Update metrics
            self.redis_client.hincrby("circuit_breaker_metrics", "total_requests", 1)
            self.redis_client.hincrby("circuit_breaker_metrics", "failed_requests", 1)
            
            # Increment failure count
            failures = self.redis_client.incr(f"circuit_breaker:failures:{operation}")
            
            # Get error pattern
            pattern = self._get_error_pattern(operation)
            if pattern:
                threshold = pattern.get("circuit_breaker", {}).get("threshold", 3)
                
                # Open circuit if threshold exceeded
                if failures >= threshold:
                    self._set_circuit_state(operation, "open")
                    self.redis_client.hincrby("circuit_breaker_metrics", "circuit_opens", 1)
                    
                    # Set timeout
                    timeout = pattern.get("circuit_breaker", {}).get("timeout", 300)
                    self.redis_client.setex(
                        f"circuit_breaker:timeout:{operation}",
                        timeout,
                        "1"
                    )
                    
        except Exception as e:
            logger.error(f"Error recording failure for {operation}", exc_info=True)
            
    def _get_circuit_state(self, operation: str) -> str:
        """Get current circuit state"""
        try:
            state = self.redis_client.get(f"circuit_breaker:state:{operation}")
            return state or "closed"
        except Exception:
            return "closed"
            
    def _set_circuit_state(self, operation: str, state: str):
        """Set circuit state"""
        try:
            self.redis_client.set(f"circuit_breaker:state:{operation}", state)
        except Exception as e:
            logger.error(f"Error setting circuit state for {operation}", exc_info=True)
            
    def _should_allow_half_open(self, operation: str) -> bool:
        """Check if circuit should transition to half-open state"""
        try:
            # Check if timeout has expired
            timeout_key = f"circuit_breaker:timeout:{operation}"
            if not self.redis_client.exists(timeout_key):
                return True
            return False
        except Exception:
            return False
            
    def _should_allow_half_open_request(self, operation: str) -> bool:
        """Check if request should be allowed in half-open state"""
        try:
            # Get error pattern
            pattern = self._get_error_pattern(operation)
            if pattern:
                # Allow limited requests in half-open state
                half_open_timeout = pattern.get("circuit_breaker", {}).get("half_open_timeout", 60)
                key = f"circuit_breaker:half_open:{operation}"
                
                # Check if we're within the half-open timeout
                if not self.redis_client.exists(key):
                    self.redis_client.setex(key, half_open_timeout, "1")
                    self.redis_client.hincrby("circuit_breaker_metrics", "half_open_attempts", 1)
                    return True
                    
            return False
        except Exception:
            return False
            
    def _get_error_pattern(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get error pattern for operation"""
        try:
            # Extract error type from operation
            error_type = operation.split("_")[0]
            
            # Load error patterns
            with open('config/error_patterns.yaml', 'r') as f:
                import yaml
                patterns = yaml.safe_load(f)
                return patterns.get(error_type)
        except Exception:
            return None
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        try:
            metrics = self.redis_client.hgetall("circuit_breaker_metrics")
            return {
                "total_requests": int(metrics.get("total_requests", 0)),
                "failed_requests": int(metrics.get("failed_requests", 0)),
                "successful_requests": int(metrics.get("successful_requests", 0)),
                "circuit_opens": int(metrics.get("circuit_opens", 0)),
                "circuit_closes": int(metrics.get("circuit_closes", 0)),
                "half_open_attempts": int(metrics.get("half_open_attempts", 0)),
                "failure_rate": self._calculate_failure_rate(metrics)
            }
        except Exception as e:
            logger.error("Error getting circuit breaker metrics", exc_info=True)
            return {}
            
    def _calculate_failure_rate(self, metrics: Dict[str, str]) -> float:
        """Calculate failure rate"""
        try:
            total = int(metrics.get("total_requests", 0))
            if total == 0:
                return 0.0
            return (int(metrics.get("failed_requests", 0)) / total) * 100
        except Exception:
            return 0.0 