import os
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
from .config import settings

logger = logging.getLogger(__name__)

class LLMLoadBalancer:
    def __init__(self):
        self.instances: List[Dict[str, Any]] = []
        self.current_index = 0
        self.health_check_interval = 30  # seconds
        self.instance_timeout = 5  # seconds
        self._initialize_instances()

    def _initialize_instances(self):
        """Initialize LLM instances from environment variables"""
        # Add primary Ollama instance
        self.instances.append({
            "url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "healthy": True,
            "last_used": datetime.now(),
            "request_count": 0,
            "avg_latency": 0
        })

        # Add additional instances if configured
        additional_instances = os.getenv("ADDITIONAL_OLLAMA_INSTANCES", "").split(",")
        for instance in additional_instances:
            if instance.strip():
                self.instances.append({
                    "url": instance.strip(),
                    "model": settings.OLLAMA_MODEL,
                    "healthy": True,
                    "last_used": datetime.now(),
                    "request_count": 0,
                    "avg_latency": 0
                })

    async def start_health_check(self):
        """Start periodic health checks for all instances"""
        while True:
            await self._check_instances_health()
            await asyncio.sleep(self.health_check_interval)

    async def _check_instances_health(self):
        """Check health of all LLM instances"""
        async with aiohttp.ClientSession() as session:
            for instance in self.instances:
                try:
                    async with session.get(f"{instance['url']}/api/version", timeout=self.instance_timeout) as response:
                        instance["healthy"] = response.status == 200
                except Exception as e:
                    logger.warning(f"Health check failed for {instance['url']}: {str(e)}")
                    instance["healthy"] = False

    def get_next_instance(self) -> Optional[Dict[str, Any]]:
        """Get next available LLM instance using round-robin with health checks"""
        healthy_instances = [i for i in self.instances if i["healthy"]]
        if not healthy_instances:
            return None

        # Round-robin selection
        instance = healthy_instances[self.current_index]
        self.current_index = (self.current_index + 1) % len(healthy_instances)
        
        # Update instance stats
        instance["last_used"] = datetime.now()
        instance["request_count"] += 1
        
        return instance

    def update_instance_stats(self, instance_url: str, latency: float):
        """Update instance statistics after a request"""
        for instance in self.instances:
            if instance["url"] == instance_url:
                # Update average latency using exponential moving average
                alpha = 0.1  # smoothing factor
                instance["avg_latency"] = (alpha * latency) + ((1 - alpha) * instance["avg_latency"])
                break

    def get_instance_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all instances"""
        return [{
            "url": i["url"],
            "model": i["model"],
            "healthy": i["healthy"],
            "request_count": i["request_count"],
            "avg_latency": i["avg_latency"],
            "last_used": i["last_used"].isoformat()
        } for i in self.instances]

    def get_optimal_instance(self) -> Optional[Dict[str, Any]]:
        """Get the optimal instance based on health and performance"""
        healthy_instances = [i for i in self.instances if i["healthy"]]
        if not healthy_instances:
            return None

        # Sort by average latency and request count
        return min(healthy_instances, key=lambda x: (x["avg_latency"], x["request_count"])) 