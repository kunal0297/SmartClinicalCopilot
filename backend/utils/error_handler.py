import logging
import traceback
import sys
from typing import Dict, Any, Optional, Type, Callable
from datetime import datetime
from functools import wraps
import json
from dataclasses import dataclass, asdict
from .metrics import PerformanceMetrics, SecurityMetrics

logger = logging.getLogger(__name__)

@dataclass
class ErrorContext:
    """Context information for an error"""
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: datetime
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    system_state: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None

class ErrorHandler:
    """Advanced error handling system"""
    
    def __init__(self):
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_callbacks: Dict[str, Callable] = {}
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def register_error_pattern(
        self,
        pattern: str,
        severity: str,
        recovery_strategy: Optional[Callable] = None,
        callback: Optional[Callable] = None
    ):
        """Register an error pattern with its handling strategy"""
        self.error_patterns[pattern] = {
            'severity': severity,
            'recovery_strategy': recovery_strategy,
            'callback': callback
        }
        
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """Handle an error with context"""
        try:
            # Create error context
            error_context = ErrorContext(
                error_type=type(error).__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                timestamp=datetime.utcnow(),
                **(context or {})
            )
            
            # Log error
            self._log_error(error_context)
            
            # Update metrics
            self._update_metrics(error_context)
            
            # Try recovery
            if self._should_attempt_recovery(error_context):
                self._attempt_recovery(error_context)
            
            # Execute callback if registered
            self._execute_callback(error_context)
            
            return error_context
            
        except Exception as e:
            logger.error("Error in error handler", exc_info=True)
            return ErrorContext(
                error_type="ErrorHandlerError",
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                timestamp=datetime.utcnow()
            )
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with context"""
        try:
            log_data = asdict(error_context)
            log_data['timestamp'] = log_data['timestamp'].isoformat()
            
            if error_context.error_type in self.error_patterns:
                pattern = self.error_patterns[error_context.error_type]
                severity = pattern['severity']
                
                if severity == 'critical':
                    logger.critical(json.dumps(log_data))
                elif severity == 'error':
                    logger.error(json.dumps(log_data))
                elif severity == 'warning':
                    logger.warning(json.dumps(log_data))
                else:
                    logger.info(json.dumps(log_data))
            else:
                logger.error(json.dumps(log_data))
                
        except Exception as e:
            logger.error("Error logging error context", exc_info=True)
    
    def _update_metrics(self, error_context: ErrorContext):
        """Update metrics based on error"""
        try:
            # Update performance metrics
            PerformanceMetrics.update_error_rates(
                1,
                error_context.error_type
            )
            
            # Update security metrics if applicable
            if error_context.error_type in [
                'AuthenticationError',
                'AuthorizationError',
                'SecurityError'
            ]:
                SecurityMetrics.update_suspicious_activities(
                    1,
                    error_context.error_type
                )
                
        except Exception as e:
            logger.error("Error updating metrics", exc_info=True)
    
    def _should_attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Determine if recovery should be attempted"""
        try:
            if error_context.error_type not in self.error_patterns:
                return False
                
            pattern = self.error_patterns[error_context.error_type]
            return pattern['recovery_strategy'] is not None
            
        except Exception as e:
            logger.error("Error checking recovery possibility", exc_info=True)
            return False
    
    def _attempt_recovery(self, error_context: ErrorContext):
        """Attempt to recover from error"""
        try:
            pattern = self.error_patterns[error_context.error_type]
            recovery_strategy = pattern['recovery_strategy']
            
            for attempt in range(self.max_retries):
                try:
                    recovery_strategy(error_context)
                    logger.info(
                        f"Recovery successful for {error_context.error_type} "
                        f"on attempt {attempt + 1}"
                    )
                    return
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"Recovery attempt {attempt + 1} failed, retrying..."
                        )
                        time.sleep(self.retry_delay * (attempt + 1))
                    else:
                        logger.error(
                            f"All recovery attempts failed for "
                            f"{error_context.error_type}"
                        )
                        
        except Exception as e:
            logger.error("Error in recovery attempt", exc_info=True)
    
    def _execute_callback(self, error_context: ErrorContext):
        """Execute registered callback for error"""
        try:
            if error_context.error_type in self.error_patterns:
                pattern = self.error_patterns[error_context.error_type]
                callback = pattern['callback']
                
                if callback:
                    callback(error_context)
                    
        except Exception as e:
            logger.error("Error executing error callback", exc_info=True)

def handle_errors(error_handler: ErrorHandler):
    """Decorator for handling errors in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'endpoint': func.__name__,
                    'request_data': {
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }
                }
                error_handler.handle_error(e, context)
                raise
        return wrapper
    return decorator

# Initialize global error handler
error_handler = ErrorHandler()

# Register common error patterns
error_handler.register_error_pattern(
    'DatabaseError',
    'error',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'AuthenticationError',
    'warning',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'AuthorizationError',
    'warning',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'ValidationError',
    'warning',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'NetworkError',
    'error',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'TimeoutError',
    'error',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'ResourceError',
    'error',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
)

error_handler.register_error_pattern(
    'SecurityError',
    'critical',
    recovery_strategy=lambda ctx: None,  # Implement recovery
    callback=lambda ctx: None  # Implement callback
) 