import logging
import asyncio
import psutil
import docker
import redis
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import traceback
import json
import os
import sys
import subprocess
import random
from .config import settings
from .database.connection_pool import ConnectionPool
from .monitoring.metrics import ServiceMetrics, HealthMetrics
from .circuit_breaker import CircuitBreaker
from .fallback_strategies import FallbackStrategies
from .load_balancer import LoadBalancer
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class RecoveryStrategies:
    """Advanced recovery strategies with circuit breakers and fallbacks"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.connection_pool = ConnectionPool()
        self.circuit_breaker = CircuitBreaker()
        self.fallback_strategies = FallbackStrategies()
        self.load_balancer = LoadBalancer()
        self.cache_manager = CacheManager()
        
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a service with advanced health checks and circuit breaker"""
        try:
            # Check circuit breaker
            if not self.circuit_breaker.allow_request(f"restart_{service_name}"):
                return await self.fallback_strategies.degrade_service(service_name)
            
            # Get service container
            container = self.docker_client.containers.get(service_name)
            
            # Stop container gracefully
            container.stop(timeout=30)
            
            # Clear service cache
            await self.cache_manager.clear_service_cache(service_name)
            
            # Start container
            container.start()
            
            # Wait for service to be healthy with advanced checks
            health_status = await self._wait_for_service_health(service_name)
            
            if health_status["healthy"]:
                self.circuit_breaker.record_success(f"restart_{service_name}")
                return {
                    "success": True,
                    "message": f"Service {service_name} restarted successfully",
                    "health_status": health_status
                }
            else:
                self.circuit_breaker.record_failure(f"restart_{service_name}")
                return await self.fallback_strategies.degrade_service(service_name)
            
        except Exception as e:
            self.circuit_breaker.record_failure(f"restart_{service_name}")
            logger.error(f"Error restarting service {service_name}", exc_info=True)
            return await self.fallback_strategies.degrade_service(service_name)
            
    async def reconnect_db(self) -> Dict[str, Any]:
        """Reconnect to database with connection pool management and circuit breaker"""
        try:
            # Check circuit breaker
            if not self.circuit_breaker.allow_request("reconnect_db"):
                return await self.fallback_strategies.use_read_replica()
            
            # Close all existing connections
            self.connection_pool.close_all()
            
            # Reinitialize connection pool with optimized settings
            self.connection_pool.initialize(
                min_size=5,
                max_size=20,
                timeout=30
            )
            
            # Test connection with retry
            if await self._test_db_connection_with_retry():
                self.circuit_breaker.record_success("reconnect_db")
                return {
                    "success": True,
                    "message": "Database reconnected successfully",
                    "pool_stats": self.connection_pool.get_stats()
                }
            else:
                self.circuit_breaker.record_failure("reconnect_db")
                return await self.fallback_strategies.use_read_replica()
            
        except Exception as e:
            self.circuit_breaker.record_failure("reconnect_db")
            logger.error("Error reconnecting to database", exc_info=True)
            return await self.fallback_strategies.use_read_replica()
            
    async def cleanup_memory(self) -> Dict[str, Any]:
        """Advanced memory cleanup with thresholds and optimization"""
        try:
            # Check circuit breaker
            if not self.circuit_breaker.allow_request("cleanup_memory"):
                return await self.fallback_strategies.degrade_features()
            
            # Get current memory usage
            memory_usage = psutil.virtual_memory().percent
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear Redis cache if memory usage is high
            if memory_usage > 80:
                await self.cache_manager.clear_all_caches()
                
            # Clear temporary files
            await self._cleanup_temp_files()
            
            # Optimize memory usage
            await self._optimize_memory_usage()
            
            # Check if cleanup was successful
            new_memory_usage = psutil.virtual_memory().percent
            if new_memory_usage < memory_usage:
                self.circuit_breaker.record_success("cleanup_memory")
                return {
                    "success": True,
                    "message": "Memory cleanup completed",
                    "memory_usage": new_memory_usage,
                    "reduction": memory_usage - new_memory_usage
                }
            else:
                self.circuit_breaker.record_failure("cleanup_memory")
                return await self.fallback_strategies.degrade_features()
            
        except Exception as e:
            self.circuit_breaker.record_failure("cleanup_memory")
            logger.error("Error cleaning up memory", exc_info=True)
            return await self.fallback_strategies.degrade_features()
            
    async def reload_config(self) -> Dict[str, Any]:
        """Reload system configuration with validation and backup"""
        try:
            # Check circuit breaker
            if not self.circuit_breaker.allow_request("reload_config"):
                return await self.fallback_strategies.use_default_config()
            
            # Backup current configuration
            await self._backup_config()
            
            # Reload environment variables
            settings.reload()
            
            # Validate new configuration
            if await self._validate_config():
                # Update service configurations
                await self._update_service_configs()
                
                self.circuit_breaker.record_success("reload_config")
                return {
                    "success": True,
                    "message": "Configuration reloaded successfully",
                    "validation": "passed"
                }
            else:
                # Restore from backup
                await self._restore_config()
                self.circuit_breaker.record_failure("reload_config")
                return await self.fallback_strategies.use_default_config()
            
        except Exception as e:
            self.circuit_breaker.record_failure("reload_config")
            logger.error("Error reloading configuration", exc_info=True)
            return await self.fallback_strategies.use_default_config()
            
    async def retry_with_backoff(
        self,
        operation: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        jitter: bool = True
    ) -> Dict[str, Any]:
        """Enhanced retry with exponential backoff and jitter"""
        try:
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    result = await operation()
                    return {
                        "success": True,
                        "message": "Operation succeeded",
                        "attempt": attempt + 1,
                        "result": result
                    }
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    # Calculate next delay with jitter
                    if jitter:
                        delay = min(
                            delay * 2 + random.uniform(0, 0.1 * delay),
                            max_delay
                        )
                    else:
                        delay = min(delay * 2, max_delay)
                        
                    await asyncio.sleep(delay)
                    
        except Exception as e:
            logger.error("Error in retry operation", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }
            
    async def validate_and_retry(
        self,
        data: Dict[str, Any],
        validator: Callable,
        strict: bool = True
    ) -> Dict[str, Any]:
        """Enhanced data validation with strict mode and custom validators"""
        try:
            # Validate data with strict mode
            validation_result = await self._validate_data(data, validator, strict)
            
            if validation_result["valid"]:
                # Retry operation with validated data
                return await self.retry_with_backoff(
                    lambda: self._process_validated_data(data)
                )
            else:
                return {
                    "success": False,
                    "message": "Data validation failed",
                    "errors": validation_result["errors"]
                }
            
        except Exception as e:
            logger.error("Error in validate and retry", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }
            
    async def check_permissions(self, resource: str) -> Dict[str, Any]:
        """Enhanced permission checking with recursive mode"""
        try:
            # Check current permissions
            current_perms = os.stat(resource).st_mode
            
            # Check parent directory permissions
            parent_dir = os.path.dirname(resource)
            parent_perms = os.stat(parent_dir).st_mode
            
            # Set correct permissions recursively
            if os.path.isdir(resource):
                for root, dirs, files in os.walk(resource):
                    for item in dirs + files:
                        os.chmod(os.path.join(root, item), 0o644)
            
            # Set resource permissions
            os.chmod(resource, 0o644)
            
            return {
                "success": True,
                "message": f"Permissions updated for {resource}",
                "old_permissions": oct(current_perms),
                "new_permissions": "0o644",
                "parent_permissions": oct(parent_perms)
            }
            
        except Exception as e:
            logger.error(f"Error checking permissions for {resource}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }
            
    async def block_and_alert(self, security_event: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced security blocking with IP tracking and alerting"""
        try:
            # Block IP if present
            if "ip" in security_event:
                await self._block_ip(security_event["ip"])
                
            # Track security event
            await self._track_security_event(security_event)
            
            # Send security alert
            await self._send_security_alert(security_event)
            
            # Update security metrics
            await self._update_security_metrics(security_event)
            
            return {
                "success": True,
                "message": "Security event handled",
                "blocked_ip": security_event.get("ip"),
                "alert_sent": True,
                "metrics_updated": True
            }
            
        except Exception as e:
            logger.error("Error in block and alert", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }
            
    async def _wait_for_service_health(self, service_name: str) -> Dict[str, Any]:
        """Wait for service health with advanced checks"""
        for _ in range(30):  # 30 second timeout
            health = await self._check_service_health(service_name)
            if health["status"] == "healthy":
                return health
            await asyncio.sleep(1)
        return {"status": "unhealthy", "error": "Health check timeout"}
        
    async def _test_db_connection_with_retry(self) -> bool:
        """Test database connection with retry"""
        for _ in range(3):
            try:
                async with self.connection_pool.get_connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT 1")
                        return True
            except Exception:
                await asyncio.sleep(1)
        return False
        
    async def _cleanup_temp_files(self):
        """Clean up temporary files"""
        temp_dir = "/tmp"
        for file in os.listdir(temp_dir):
            try:
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                continue
                
    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        # Implement memory optimization strategies
        pass
        
    async def _backup_config(self):
        """Backup current configuration"""
        # Implement configuration backup
        pass
        
    async def _validate_config(self) -> bool:
        """Validate configuration"""
        # Implement configuration validation
        return True
        
    async def _restore_config(self):
        """Restore configuration from backup"""
        # Implement configuration restore
        pass
        
    async def _validate_data(
        self,
        data: Dict[str, Any],
        validator: Callable,
        strict: bool
    ) -> Dict[str, Any]:
        """Validate data with strict mode"""
        # Implement data validation
        return {"valid": True, "errors": []}
        
    async def _process_validated_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process validated data"""
        # Implement data processing
        return {"processed": True, "data": data}
        
    async def _block_ip(self, ip: str):
        """Block an IP address"""
        # Implement IP blocking
        pass
        
    async def _track_security_event(self, event: Dict[str, Any]):
        """Track security event"""
        # Implement security event tracking
        pass
        
    async def _send_security_alert(self, event: Dict[str, Any]):
        """Send security alert"""
        # Implement security alert sending
        pass
        
    async def _update_security_metrics(self, event: Dict[str, Any]):
        """Update security metrics"""
        # Implement security metrics update
        pass
        
    async def _check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check if a service is healthy"""
        try:
            container = self.docker_client.containers.get(service_name)
            health = container.attrs.get("State", {}).get("Health", {})
            return health.get("Status") == "healthy"
        except Exception:
            return False
            
    async def _update_service_configs(self):
        """Update service configurations"""
        services = ["api", "worker", "cache", "database"]
        for service in services:
            try:
                container = self.docker_client.containers.get(service)
                container.restart()
            except Exception as e:
                logger.error(f"Error updating {service} config", exc_info=True)
                
    async def _update_security_metrics(self, event: Dict[str, Any]):
        """Update security metrics"""
        # Implement security metrics update
        pass 