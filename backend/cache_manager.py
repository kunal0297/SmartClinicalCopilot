import logging
import json
import time
from typing import Dict, Any, Optional, List
import redis
from .config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache manager for handling data caching and retrieval"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour default TTL
        
    async def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data for a given key"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached data for key {key}", exc_info=True)
            return None
            
    async def set_cached_data(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set cached data with optional TTL"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(
                key,
                ttl,
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"Error setting cached data for key {key}", exc_info=True)
            return False
            
    async def get_cache_age(self, key: str) -> Optional[int]:
        """Get age of cached data in seconds"""
        try:
            ttl = self.redis_client.ttl(key)
            if ttl > 0:
                return self.default_ttl - ttl
            return None
            
        except Exception as e:
            logger.error(f"Error getting cache age for key {key}", exc_info=True)
            return None
            
    async def invalidate_cache(self, key: str) -> bool:
        """Invalidate cached data"""
        try:
            return bool(self.redis_client.delete(key))
            
        except Exception as e:
            logger.error(f"Error invalidating cache for key {key}", exc_info=True)
            return False
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                "total_keys": info.get("db0", {}).get("keys", 0),
                "used_memory": info.get("used_memory_human", "0"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            logger.error("Error getting cache stats", exc_info=True)
            return {}
            
    async def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            # Redis automatically removes expired keys
            return 0
            
        except Exception as e:
            logger.error("Error clearing expired cache", exc_info=True)
            return 0
            
    async def get_cache_keys(self, pattern: str = "*") -> List[str]:
        """Get list of cache keys matching pattern"""
        try:
            return self.redis_client.keys(pattern)
            
        except Exception as e:
            logger.error(f"Error getting cache keys for pattern {pattern}", exc_info=True)
            return []
            
    async def get_cache_size(self) -> int:
        """Get total number of cache entries"""
        try:
            return len(await self.get_cache_keys())
            
        except Exception as e:
            logger.error("Error getting cache size", exc_info=True)
            return 0
            
    async def get_cache_memory_usage(self) -> str:
        """Get cache memory usage"""
        try:
            info = self.redis_client.info()
            return info.get("used_memory_human", "0")
            
        except Exception as e:
            logger.error("Error getting cache memory usage", exc_info=True)
            return "0"
            
    async def get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        try:
            info = self.redis_client.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            return hits / total if total > 0 else 0.0
            
        except Exception as e:
            logger.error("Error getting cache hit rate", exc_info=True)
            return 0.0
            
    async def get_cache_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a cache key"""
        try:
            return self.redis_client.ttl(key)
            
        except Exception as e:
            logger.error(f"Error getting cache TTL for key {key}", exc_info=True)
            return None
            
    async def set_cache_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for a cache key"""
        try:
            return bool(self.redis_client.expire(key, ttl))
            
        except Exception as e:
            logger.error(f"Error setting cache TTL for key {key}", exc_info=True)
            return False
            
    async def get_cache_type(self, key: str) -> Optional[str]:
        """Get type of cached data"""
        try:
            return self.redis_client.type(key)
            
        except Exception as e:
            logger.error(f"Error getting cache type for key {key}", exc_info=True)
            return None
            
    async def get_cache_value_size(self, key: str) -> Optional[int]:
        """Get size of cached value in bytes"""
        try:
            return self.redis_client.memory_usage(key)
            
        except Exception as e:
            logger.error(f"Error getting cache value size for key {key}", exc_info=True)
            return None 