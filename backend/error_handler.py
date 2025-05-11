import logging
import traceback
import json
import os
import sys
import subprocess
import docker
import requests
import yaml
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import redis
from .config import settings
from .llm_service import LLMService
from .logging_config import LogContext
from .recovery_strategies import RecoveryStrategies
import asyncio
import psutil

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.docker_client = docker.from_env()
        self.llm_service = LLMService()
        self.recovery_strategies = RecoveryStrategies()
        self.error_patterns = self._load_error_patterns()
        self._setup_logging()
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize error metrics in Redis"""
        metrics = {
            "total_errors": 0,
            "recovery_attempts": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "last_error_time": None,
            "error_types": {},
            "recovery_success_rate": 0,
            "system_health": {}
        }
        self.redis_client.hmset("error_metrics", metrics)

    def _setup_logging(self):
        """Setup enhanced logging configuration"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File handler for detailed logs
        file_handler = logging.FileHandler(
            f"{log_dir}/error_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        # Stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(stream_handler)

    def _load_error_patterns(self) -> Dict[str, Any]:
        """Load error pattern recognition rules"""
        try:
            with open('config/error_patterns.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error("Error patterns file not found")
            return {}

    async def handle_exception(self, request: Request, exc: Exception) -> Response:
        """Enhanced global exception handler for FastAPI"""
        error_id = self._generate_error_id()
        
        with LogContext(
            error_id=error_id,
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__
        ):
            # Capture error context
            error_context = await self._capture_error_context(request, exc)
            
            # Log error details
            self._log_error(error_id, exc, error_context)
            
            # Store error in Redis for monitoring
            self._store_error_metrics(error_id, exc, error_context)
            
            # Attempt auto-recovery with retries
            recovery_result = await self._attempt_recovery_with_retries(exc, error_context)
            
            # Generate user-friendly response
            return self._generate_error_response(error_id, exc, recovery_result)

    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

    async def _capture_error_context(self, request: Request, exc: Exception) -> Dict[str, Any]:
        """Capture detailed error context"""
        try:
            # Get request details
            body = await request.body()
            headers = dict(request.headers)
            
            # Remove sensitive information
            if 'authorization' in headers:
                headers['authorization'] = '***'
            if 'cookie' in headers:
                headers['cookie'] = '***'
                
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
                "method": request.method,
                "headers": headers,
                "body": body.decode() if body else None,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "stack_trace": traceback.format_exc(),
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "memory_usage": psutil.virtual_memory().percent,
                    "cpu_usage": psutil.cpu_percent()
                }
            }
        except Exception as e:
            logger.error("Error capturing context", exc_info=True)
            return {
                "error": "Failed to capture context",
                "context_error": str(e)
            }

    def _log_error(self, error_id: str, exc: Exception, context: Dict[str, Any]):
        """Log error with context"""
        try:
            log_data = {
                "error_id": error_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "context": context
            }
            
            # Get error pattern
            pattern = self.error_patterns.get(type(exc).__name__, {})
            severity = pattern.get("severity", "error")
            
            # Log based on severity
            if severity == "critical":
                logger.critical(json.dumps(log_data))
            elif severity == "error":
                logger.error(json.dumps(log_data))
            elif severity == "warning":
                logger.warning(json.dumps(log_data))
            else:
                logger.info(json.dumps(log_data))
                
        except Exception as e:
            logger.error("Error logging error", exc_info=True)

    def _store_error_metrics(self, error_id: str, exc: Exception, context: Dict[str, Any]):
        """Store error metrics for monitoring"""
        try:
            error_type = type(exc).__name__
            
            # Increment error counters
            self.redis_client.hincrby("error_metrics", "total_errors", 1)
            self.redis_client.hincrby("error_metrics:types", error_type, 1)
            
            # Update last error time
            self.redis_client.hset(
                "error_metrics",
                "last_error_time",
                datetime.utcnow().isoformat()
            )
            
            # Store detailed metrics
            metrics = {
                "error_id": error_id,
                "error_type": error_type,
                "timestamp": context["timestamp"],
                "path": context["path"],
                "method": context["method"],
                "system_info": json.dumps(context["system_info"])
            }
            
            self.redis_client.hset(
                f"error_details:{error_id}",
                mapping=metrics
            )
            
            # Update system health metrics
            self._update_system_health_metrics()
            
        except Exception as e:
            logger.error("Error storing metrics", exc_info=True)

    async def _attempt_recovery_with_retries(
        self,
        exc: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt recovery with configurable retries"""
        error_type = type(exc).__name__
        pattern = self.error_patterns.get(error_type)
        
        if not pattern or not pattern.get("auto_fix", True):
            return {"success": False, "reason": "No recovery pattern found"}
            
        action = pattern.get("action")
        retry_count = pattern.get("retry_count", 1)
        retry_delay = pattern.get("retry_delay", 0)
        recovery_strategy = pattern.get("recovery_strategy")
        
        # Increment recovery attempts
        self.redis_client.hincrby("error_metrics", "recovery_attempts", 1)
        
        for attempt in range(retry_count):
            with LogContext(
                attempt=attempt + 1,
                max_attempts=retry_count,
                action=action,
                strategy=recovery_strategy
            ):
                try:
                    # Execute recovery strategy
                    result = await self._execute_recovery_strategy(
                        recovery_strategy,
                        exc,
                        context
                    )
                    
                    if result["success"]:
                        # Increment successful recoveries
                        self.redis_client.hincrby(
                            "error_metrics",
                            "successful_recoveries",
                            1
                        )
                        logger.info("Recovery successful", extra=result)
                        return result
                        
                    if attempt < retry_count - 1:
                        logger.warning(
                            f"Recovery attempt {attempt + 1} failed, retrying...",
                            extra=result
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        # Increment failed recoveries
                        self.redis_client.hincrby(
                            "error_metrics",
                            "failed_recoveries",
                            1
                        )
                        logger.error("All recovery attempts failed", extra=result)
                        return result
                        
                except Exception as e:
                    logger.error(
                        f"Error during recovery attempt {attempt + 1}",
                        exc_info=True,
                        extra={"error": str(e)}
                    )
                    if attempt == retry_count - 1:
                        return {
                            "success": False,
                            "reason": f"Recovery failed: {str(e)}"
                        }
                    await asyncio.sleep(retry_delay)
        
        return {"success": False, "reason": "Max retries exceeded"}

    async def _execute_recovery_strategy(
        self,
        strategy: str,
        exc: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute recovery strategy based on error type"""
        try:
            if strategy == "restart_service":
                return await self.recovery_strategies.restart_service(
                    context.get("service_name", "api")
                )
            elif strategy == "reconnect_db":
                return await self.recovery_strategies.reconnect_db()
            elif strategy == "cleanup_memory":
                return await self.recovery_strategies.cleanup_memory()
            elif strategy == "reload_config":
                return await self.recovery_strategies.reload_config()
            elif strategy == "check_permissions":
                return await self.recovery_strategies.check_permissions(
                    context.get("resource")
                )
            elif strategy == "block_and_alert":
                return await self.recovery_strategies.block_and_alert(context)
            elif strategy == "retry_with_backoff":
                return await self.recovery_strategies.retry_with_backoff(
                    context.get("operation")
                )
            elif strategy == "validate_and_retry":
                return await self.recovery_strategies.validate_and_retry(
                    context.get("data"),
                    context.get("validator")
                )
            else:
                return {"success": False, "reason": "Unknown recovery strategy"}
                
        except Exception as e:
            logger.error(f"Error executing recovery strategy {strategy}", exc_info=True)
            return {"success": False, "reason": str(e)}

    def _generate_error_response(
        self,
        error_id: str,
        exc: Exception,
        recovery_result: Dict[str, Any]
    ) -> JSONResponse:
        """Generate user-friendly error response"""
        error_type = type(exc).__name__
        pattern = self.error_patterns.get(error_type, {})
        
        response = {
            "error_id": error_id,
            "type": error_type,
            "message": str(exc),
            "severity": pattern.get("severity", "medium"),
            "recovery": {
                "attempted": bool(recovery_result),
                "successful": recovery_result.get("success", False),
                "action": recovery_result.get("action"),
                "details": recovery_result.get("details", {})
            },
            "timestamp": datetime.utcnow().isoformat(),
            "support": {
                "contact": settings.SUPPORT_EMAIL,
                "documentation": settings.API_DOCS_URL
            }
        }
        
        # Add helpful suggestions based on error type
        response["suggestions"] = self._get_error_suggestions(error_type, exc)
        
        return JSONResponse(
            status_code=500,
            content=response
        )

    def _get_error_suggestions(self, error_type: str, exc: Exception) -> List[str]:
        """Get helpful suggestions based on error type"""
        suggestions = []
        
        if error_type == "DatabaseError":
            suggestions.extend([
                "Check database connection settings",
                "Verify database server is running",
                "Check database user permissions"
            ])
        elif error_type == "ValidationError":
            suggestions.extend([
                "Review input data format",
                "Check required fields",
                "Verify data types"
            ])
        elif error_type == "ConnectionError":
            suggestions.extend([
                "Check network connectivity",
                "Verify service endpoints",
                "Check firewall settings"
            ])
        elif error_type == "MemoryError":
            suggestions.extend([
                "Check system memory usage",
                "Clear application cache",
                "Optimize memory-intensive operations"
            ])
        elif error_type == "PermissionError":
            suggestions.extend([
                "Check file/directory permissions",
                "Verify user access rights",
                "Check security policies"
            ])
            
        return suggestions

    def _update_system_health_metrics(self):
        """Update system health metrics"""
        try:
            health_metrics = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.redis_client.hset(
                "error_metrics",
                "system_health",
                json.dumps(health_metrics)
            )
            
        except Exception as e:
            logger.error("Error updating system health metrics", exc_info=True)

    def get_error_metrics(self) -> Dict[str, Any]:
        """Get enhanced error metrics for monitoring"""
        try:
            metrics = {
                "total_errors": int(self.redis_client.hget("error_metrics", "total_errors") or 0),
                "recovery_attempts": int(self.redis_client.hget("error_metrics", "recovery_attempts") or 0),
                "successful_recoveries": int(self.redis_client.hget("error_metrics", "successful_recoveries") or 0),
                "failed_recoveries": int(self.redis_client.hget("error_metrics", "failed_recoveries") or 0),
                "last_error_time": self.redis_client.hget("error_metrics", "last_error_time"),
                "error_types": {},
                "recovery_success_rate": 0,
                "recent_errors": [],
                "system_health": {}
            }
            
            # Get error type counts
            error_counts = self.redis_client.hgetall("error_metrics:types")
            metrics["error_types"] = {
                k: int(v) for k, v in error_counts.items()
            }
            
            # Calculate recovery success rate
            if metrics["recovery_attempts"] > 0:
                metrics["recovery_success_rate"] = (
                    metrics["successful_recoveries"] / metrics["recovery_attempts"]
                ) * 100
            
            # Get recent errors
            recent_errors = self.redis_client.lrange("error_logs", 0, 9)
            metrics["recent_errors"] = [
                json.loads(error) for error in recent_errors
            ]
            
            # Get system health metrics
            system_health = self.redis_client.hget("error_metrics", "system_health")
            if system_health:
                metrics["system_health"] = json.loads(system_health)
            
            return metrics
            
        except Exception as e:
            logger.error("Error getting metrics", exc_info=True)
            return {} 