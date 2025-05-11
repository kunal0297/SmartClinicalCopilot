import logging
import asyncio
import yaml
from fastapi import FastAPI, HTTPException
from .error_handler import ErrorHandler
from .recovery_strategies import RecoveryStrategies
from .monitoring.health_monitor import HealthMonitor
from .circuit_breaker import CircuitBreaker
from .fallback_strategies import FallbackStrategies
from .load_balancer import LoadBalancer
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class SelfHealingSystem:
    """Main self-healing system implementation"""
    
    def __init__(self):
        self.app = FastAPI(title="Self-Healing System")
        self.error_handler = ErrorHandler()
        self.health_monitor = HealthMonitor()
        self.recovery_strategies = RecoveryStrategies()
        self.circuit_breaker = CircuitBreaker()
        self.fallback_strategies = FallbackStrategies()
        self.load_balancer = LoadBalancer()
        self.cache_manager = CacheManager()
        self.config = self._load_config()
        self._setup_routes()
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open("config/self_healing_config.yaml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error("Error loading configuration", exc_info=True)
            raise
            
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Get system health status"""
            try:
                health = await self.health_monitor.get_current_health()
                return health
            except Exception as e:
                logger.error("Error getting health status", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/metrics")
        async def get_metrics():
            """Get error metrics"""
            try:
                metrics = await self.error_handler.get_metrics()
                return metrics
            except Exception as e:
                logger.error("Error getting metrics", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/recover/{error_type}")
        async def recover_error(error_type: str):
            """Manually trigger recovery for an error type"""
            try:
                result = await self.error_handler.handle_exception(error_type)
                return result
            except Exception as e:
                logger.error(f"Error recovering from {error_type}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/config")
        async def get_config():
            """Get current configuration"""
            try:
                return self.config
            except Exception as e:
                logger.error("Error getting configuration", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/config/reload")
        async def reload_config():
            """Reload configuration from file"""
            try:
                self.config = self._load_config()
                return {"message": "Configuration reloaded successfully"}
            except Exception as e:
                logger.error("Error reloading configuration", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/services")
        async def get_services():
            """Get registered services"""
            try:
                services = {}
                for service_type in self.config["load_balancer"]["service_types"]:
                    services[service_type] = await self.load_balancer.get_service_stats(service_type)
                return services
            except Exception as e:
                logger.error("Error getting services", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/cache/stats")
        async def get_cache_stats():
            """Get cache statistics"""
            try:
                stats = await self.cache_manager.get_cache_stats()
                return stats
            except Exception as e:
                logger.error("Error getting cache stats", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
    async def start(self):
        """Start the self-healing system"""
        try:
            # Start health monitoring
            await self.health_monitor.start()
            
            # Start FastAPI application
            import uvicorn
            uvicorn.run(self.app, host="0.0.0.0", port=8000)
            
        except Exception as e:
            logger.error("Error starting self-healing system", exc_info=True)
            raise
            
    async def stop(self):
        """Stop the self-healing system"""
        try:
            # Stop health monitoring
            await self.health_monitor.stop()
            
        except Exception as e:
            logger.error("Error stopping self-healing system", exc_info=True)
            raise
            
if __name__ == "__main__":
    # Create and run self-healing system
    self_healing = SelfHealingSystem()
    asyncio.run(self_healing.start()) 