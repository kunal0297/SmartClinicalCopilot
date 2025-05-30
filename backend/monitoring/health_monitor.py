import logging
import asyncio
import psutil
import docker
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from prometheus_client import Counter, Gauge, Histogram
from .metrics import ServiceMetrics, HealthMetrics
from ..config import settings

logger = logging.getLogger(__name__)

# Module-level Prometheus metrics (singletons)
self_healing_errors_total = Counter('self_healing_errors_total', 'Total number of errors handled', ['error_type', 'severity'])
self_healing_recoveries_total = Counter('self_healing_recoveries_total', 'Total number of recovery attempts', ['success'])
self_healing_recovery_duration_seconds = Histogram('self_healing_recovery_duration_seconds', 'Time taken for recovery operations', ['strategy'])
self_healing_system_health = Gauge('self_healing_system_health', 'System health metrics', ['metric'])

class HealthMonitor:
    """Advanced health monitoring system"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.is_running = False
        self.metrics_history = []
        self.max_history_size = 1000
        # Use module-level metrics
        self.error_counter = self_healing_errors_total
        self.recovery_counter = self_healing_recoveries_total
        self.recovery_time = self_healing_recovery_duration_seconds
        self.system_health = self_healing_system_health
        
    async def start(self):
        """Start health monitoring"""
        self.is_running = True
        await asyncio.gather(
            self._monitor_system_metrics(),
            self._monitor_service_health(),
            self._monitor_error_rates(),
            self._cleanup_old_metrics()
        )
        
    async def stop(self):
        """Stop health monitoring"""
        self.is_running = False
        
    async def _monitor_system_metrics(self):
        """Monitor system metrics"""
        while self.is_running:
            try:
                # Collect system metrics
                metrics = {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "network_io": psutil.net_io_counters()._asdict(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Update Prometheus metrics
                self.system_health.labels('cpu').set(metrics['cpu_usage'])
                self.system_health.labels('memory').set(metrics['memory_usage'])
                self.system_health.labels('disk').set(metrics['disk_usage'])
                
                # Store metrics
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                    
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("Error monitoring system metrics", exc_info=True)
                await asyncio.sleep(5)
                
    async def _monitor_service_health(self):
        """Monitor service health"""
        while self.is_running:
            try:
                services = [
                    "api",
                    "worker",
                    "cache",
                    "database",
                    "queue"
                ]
                
                for service in services:
                    health = await self._check_service_health(service)
                    ServiceMetrics.update_health(service, health)
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Error monitoring service health", exc_info=True)
                await asyncio.sleep(5)
                
    async def _monitor_error_rates(self):
        """Monitor error rates and recovery success"""
        while self.is_running:
            try:
                # Get error metrics from Redis
                metrics = self.redis_client.hgetall("error_metrics")
                
                if metrics:
                    # Update Prometheus metrics
                    for error_type, count in metrics.get("error_types", {}).items():
                        self.error_counter.labels(
                            error_type=error_type,
                            severity=self._get_error_severity(error_type)
                        ).inc(int(count))
                        
                    # Update recovery metrics
                    recovery_attempts = int(metrics.get("recovery_attempts", 0))
                    successful_recoveries = int(metrics.get("successful_recoveries", 0))
                    
                    self.recovery_counter.labels(success="true").inc(successful_recoveries)
                    self.recovery_counter.labels(success="false").inc(
                        recovery_attempts - successful_recoveries
                    )
                    
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("Error monitoring error rates", exc_info=True)
                await asyncio.sleep(5)
                
    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        while self.is_running:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if datetime.fromisoformat(m["timestamp"]) > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error("Error cleaning up metrics", exc_info=True)
                await asyncio.sleep(300)
                
    async def _check_service_health(self, service: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            container = self.docker_client.containers.get(service)
            health = container.attrs.get("State", {}).get("Health", {})
            
            return {
                "status": "healthy" if health.get("Status") == "healthy" else "unhealthy",
                "last_check": health.get("LastCheck", {}).get("End", ""),
                "failing_streak": health.get("FailingStreak", 0),
                "log": health.get("Log", [])
            }
            
        except Exception as e:
            logger.error(f"Error checking health for {service}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    def _get_error_severity(self, error_type: str) -> str:
        """Get severity level for an error type"""
        try:
            with open('config/error_patterns.yaml', 'r') as f:
                patterns = yaml.safe_load(f)
                return patterns.get(error_type, {}).get("severity", "medium")
        except Exception:
            return "medium"
            
    def get_current_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            if not self.metrics_history:
                return {}
                
            latest_metrics = self.metrics_history[-1]
            
            return {
                "system": {
                    "cpu_usage": latest_metrics["cpu_usage"],
                    "memory_usage": latest_metrics["memory_usage"],
                    "disk_usage": latest_metrics["disk_usage"],
                    "network_io": latest_metrics["network_io"]
                },
                "services": self._get_service_status(),
                "errors": self._get_error_metrics(),
                "timestamp": latest_metrics["timestamp"]
            }
            
        except Exception as e:
            logger.error("Error getting current health", exc_info=True)
            return {}
            
    def _get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        try:
            services = {}
            for service in ["api", "worker", "cache", "database", "queue"]:
                container = self.docker_client.containers.get(service)
                services[service] = {
                    "status": container.status,
                    "health": container.attrs.get("State", {}).get("Health", {}).get("Status")
                }
            return services
        except Exception:
            return {}
            
    def _get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics"""
        try:
            metrics = self.redis_client.hgetall("error_metrics")
            return {
                "total_errors": int(metrics.get("total_errors", 0)),
                "recovery_attempts": int(metrics.get("recovery_attempts", 0)),
                "successful_recoveries": int(metrics.get("successful_recoveries", 0)),
                "failed_recoveries": int(metrics.get("failed_recoveries", 0)),
                "recovery_success_rate": float(metrics.get("recovery_success_rate", 0)),
                "error_types": json.loads(metrics.get("error_types", "{}"))
            }
        except Exception:
            return {} 