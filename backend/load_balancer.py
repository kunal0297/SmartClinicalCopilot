import logging
import random
import time
from typing import Dict, Any, List, Optional
import redis
from .config import settings

logger = logging.getLogger(__name__)

class LoadBalancer:
    """Load balancer for distributing requests across services"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.health_check_interval = 30  # 30 seconds
        self.last_health_check = 0
        
    async def get_next_service(self, service_type: str) -> Optional[str]:
        """Get next available service using round-robin"""
        try:
            # Get available services
            services = await self._get_healthy_services(service_type)
            if not services:
                return None
                
            # Get current index
            current_index = await self._get_current_index(service_type)
            
            # Calculate next index
            next_index = (current_index + 1) % len(services)
            
            # Update current index
            await self._update_current_index(service_type, next_index)
            
            return services[next_index]
            
        except Exception as e:
            logger.error(f"Error getting next service for type {service_type}", exc_info=True)
            return None
            
    async def get_random_service(self, service_type: str) -> Optional[str]:
        """Get random available service"""
        try:
            services = await self._get_healthy_services(service_type)
            return random.choice(services) if services else None
            
        except Exception as e:
            logger.error(f"Error getting random service for type {service_type}", exc_info=True)
            return None
            
    async def get_least_loaded_service(self, service_type: str) -> Optional[str]:
        """Get service with least load"""
        try:
            services = await self._get_healthy_services(service_type)
            if not services:
                return None
                
            # Get load for each service
            loads = await self._get_service_loads(services)
            
            # Find service with minimum load
            min_load_service = min(loads.items(), key=lambda x: x[1])[0]
            return min_load_service
            
        except Exception as e:
            logger.error(f"Error getting least loaded service for type {service_type}", exc_info=True)
            return None
            
    async def register_service(self, service_type: str, service_url: str) -> bool:
        """Register a new service"""
        try:
            # Add service to available services
            await self._add_service(service_type, service_url)
            
            # Initialize service metrics
            await self._init_service_metrics(service_url)
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering service {service_url}", exc_info=True)
            return False
            
    async def unregister_service(self, service_type: str, service_url: str) -> bool:
        """Unregister a service"""
        try:
            # Remove service from available services
            await self._remove_service(service_type, service_url)
            
            # Clean up service metrics
            await self._cleanup_service_metrics(service_url)
            
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering service {service_url}", exc_info=True)
            return False
            
    async def update_service_health(self, service_url: str, is_healthy: bool) -> bool:
        """Update service health status"""
        try:
            await self._set_service_health(service_url, is_healthy)
            return True
            
        except Exception as e:
            logger.error(f"Error updating health for service {service_url}", exc_info=True)
            return False
            
    async def update_service_load(self, service_url: str, load: float) -> bool:
        """Update service load"""
        try:
            await self._set_service_load(service_url, load)
            return True
            
        except Exception as e:
            logger.error(f"Error updating load for service {service_url}", exc_info=True)
            return False
            
    async def get_service_stats(self, service_type: str) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            services = await self._get_healthy_services(service_type)
            stats = {
                "total_services": len(services),
                "healthy_services": len(services),
                "service_loads": await self._get_service_loads(services),
                "service_health": await self._get_service_health(services)
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for service type {service_type}", exc_info=True)
            return {}
            
    async def _get_healthy_services(self, service_type: str) -> List[str]:
        """Get list of healthy services"""
        try:
            # Check if health check is needed
            await self._check_health_check_needed()
            
            # Get all services
            services = await self._get_services(service_type)
            
            # Filter healthy services
            healthy_services = []
            for service in services:
                if await self._is_service_healthy(service):
                    healthy_services.append(service)
                    
            return healthy_services
            
        except Exception as e:
            logger.error(f"Error getting healthy services for type {service_type}", exc_info=True)
            return []
            
    async def _get_current_index(self, service_type: str) -> int:
        """Get current service index"""
        try:
            index = self.redis_client.get(f"lb:index:{service_type}")
            return int(index) if index else 0
            
        except Exception as e:
            logger.error(f"Error getting current index for type {service_type}", exc_info=True)
            return 0
            
    async def _update_current_index(self, service_type: str, index: int):
        """Update current service index"""
        try:
            self.redis_client.set(f"lb:index:{service_type}", index)
            
        except Exception as e:
            logger.error(f"Error updating current index for type {service_type}", exc_info=True)
            
    async def _get_service_loads(self, services: List[str]) -> Dict[str, float]:
        """Get load for each service"""
        try:
            loads = {}
            for service in services:
                load = self.redis_client.get(f"lb:load:{service}")
                loads[service] = float(load) if load else 0.0
            return loads
            
        except Exception as e:
            logger.error("Error getting service loads", exc_info=True)
            return {}
            
    async def _add_service(self, service_type: str, service_url: str):
        """Add service to available services"""
        try:
            self.redis_client.sadd(f"lb:services:{service_type}", service_url)
            
        except Exception as e:
            logger.error(f"Error adding service {service_url}", exc_info=True)
            
    async def _remove_service(self, service_type: str, service_url: str):
        """Remove service from available services"""
        try:
            self.redis_client.srem(f"lb:services:{service_type}", service_url)
            
        except Exception as e:
            logger.error(f"Error removing service {service_url}", exc_info=True)
            
    async def _init_service_metrics(self, service_url: str):
        """Initialize service metrics"""
        try:
            self.redis_client.set(f"lb:health:{service_url}", 1)
            self.redis_client.set(f"lb:load:{service_url}", 0.0)
            
        except Exception as e:
            logger.error(f"Error initializing metrics for service {service_url}", exc_info=True)
            
    async def _cleanup_service_metrics(self, service_url: str):
        """Clean up service metrics"""
        try:
            self.redis_client.delete(f"lb:health:{service_url}")
            self.redis_client.delete(f"lb:load:{service_url}")
            
        except Exception as e:
            logger.error(f"Error cleaning up metrics for service {service_url}", exc_info=True)
            
    async def _set_service_health(self, service_url: str, is_healthy: bool):
        """Set service health status"""
        try:
            self.redis_client.set(f"lb:health:{service_url}", 1 if is_healthy else 0)
            
        except Exception as e:
            logger.error(f"Error setting health for service {service_url}", exc_info=True)
            
    async def _set_service_load(self, service_url: str, load: float):
        """Set service load"""
        try:
            self.redis_client.set(f"lb:load:{service_url}", load)
            
        except Exception as e:
            logger.error(f"Error setting load for service {service_url}", exc_info=True)
            
    async def _get_services(self, service_type: str) -> List[str]:
        """Get all services of a type"""
        try:
            return list(self.redis_client.smembers(f"lb:services:{service_type}"))
            
        except Exception as e:
            logger.error(f"Error getting services for type {service_type}", exc_info=True)
            return []
            
    async def _is_service_healthy(self, service_url: str) -> bool:
        """Check if service is healthy"""
        try:
            health = self.redis_client.get(f"lb:health:{service_url}")
            return bool(int(health)) if health else False
            
        except Exception as e:
            logger.error(f"Error checking health for service {service_url}", exc_info=True)
            return False
            
    async def _get_service_health(self, services: List[str]) -> Dict[str, bool]:
        """Get health status for each service"""
        try:
            health = {}
            for service in services:
                health[service] = await self._is_service_healthy(service)
            return health
            
        except Exception as e:
            logger.error("Error getting service health", exc_info=True)
            return {}
            
    async def _check_health_check_needed(self):
        """Check if health check is needed"""
        try:
            current_time = time.time()
            if current_time - self.last_health_check >= self.health_check_interval:
                await self._perform_health_check()
                self.last_health_check = current_time
                
        except Exception as e:
            logger.error("Error checking health check needed", exc_info=True)
            
    async def _perform_health_check(self):
        """Perform health check on all services"""
        try:
            # Get all service types
            service_types = self.redis_client.keys("lb:services:*")
            
            for service_type in service_types:
                # Get services for this type
                services = await self._get_services(service_type)
                
                for service in services:
                    # Check service health
                    is_healthy = await self._check_service_health(service)
                    
                    # Update health status
                    await self._set_service_health(service, is_healthy)
                    
        except Exception as e:
            logger.error("Error performing health check", exc_info=True)
            
    async def _check_service_health(self, service_url: str) -> bool:
        """Check health of a specific service"""
        try:
            # Implement actual health check logic here
            # For now, return True as placeholder
            return True
            
        except Exception as e:
            logger.error(f"Error checking health for service {service_url}", exc_info=True)
            return False 