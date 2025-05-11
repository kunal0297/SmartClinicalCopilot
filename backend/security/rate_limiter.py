import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import threading
from .metrics import SecurityMetrics

logger = logging.getLogger(__name__)

@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    period: int  # seconds
    burst: Optional[int] = None

@dataclass
class RateLimitInfo:
    """Rate limit information"""
    remaining: int
    reset: datetime
    limit: int
    burst: Optional[int]

class RateLimiter:
    """Advanced rate limiting system"""
    
    def __init__(self):
        # Rate limit configurations
        self.limits: Dict[str, RateLimit] = {
            'default': RateLimit(requests=100, period=60),
            'api': RateLimit(requests=1000, period=60),
            'auth': RateLimit(requests=5, period=60, burst=10),
            'search': RateLimit(requests=20, period=60),
            'upload': RateLimit(requests=10, period=60)
        }
        
        # Request tracking
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        
        # Locks for thread safety
        self.locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Cleanup interval
        self.cleanup_interval = 300  # 5 minutes
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self.cleanup_thread.start()
    
    def check_rate_limit(
        self,
        key: str,
        limit_type: str = 'default'
    ) -> Tuple[bool, RateLimitInfo]:
        """Check if request is within rate limit"""
        try:
            # Get rate limit configuration
            limit = self.limits.get(limit_type, self.limits['default'])
            
            # Get lock for key
            with self.locks[key]:
                # Clean old requests
                self._clean_old_requests(key, limit.period)
                
                # Get current requests
                requests = self.requests[key]
                
                # Check if within limit
                if len(requests) >= limit.requests:
                    # Check burst limit if configured
                    if limit.burst and len(requests) < limit.burst:
                        return True, self._get_rate_limit_info(
                            key,
                            limit,
                            len(requests)
                        )
                    return False, self._get_rate_limit_info(
                        key,
                        limit,
                        len(requests)
                    )
                
                # Add request
                requests.append(datetime.utcnow())
                
                # Update metrics
                SecurityMetrics.update_api_usage(1, f'rate_limit_{limit_type}')
                
                return True, self._get_rate_limit_info(
                    key,
                    limit,
                    len(requests)
                )
                
        except Exception as e:
            logger.error("Error checking rate limit", exc_info=True)
            return True, RateLimitInfo(
                remaining=0,
                reset=datetime.utcnow(),
                limit=0,
                burst=None
            )
    
    def get_rate_limit_info(
        self,
        key: str,
        limit_type: str = 'default'
    ) -> RateLimitInfo:
        """Get rate limit information"""
        try:
            # Get rate limit configuration
            limit = self.limits.get(limit_type, self.limits['default'])
            
            # Get lock for key
            with self.locks[key]:
                # Clean old requests
                self._clean_old_requests(key, limit.period)
                
                # Get current requests
                requests = self.requests[key]
                
                return self._get_rate_limit_info(
                    key,
                    limit,
                    len(requests)
                )
                
        except Exception as e:
            logger.error("Error getting rate limit info", exc_info=True)
            return RateLimitInfo(
                remaining=0,
                reset=datetime.utcnow(),
                limit=0,
                burst=None
            )
    
    def reset_rate_limit(self, key: str):
        """Reset rate limit for key"""
        try:
            # Get lock for key
            with self.locks[key]:
                # Clear requests
                self.requests[key] = []
                
        except Exception as e:
            logger.error("Error resetting rate limit", exc_info=True)
    
    def _clean_old_requests(self, key: str, period: int):
        """Clean old requests"""
        try:
            # Get current time
            current_time = datetime.utcnow()
            
            # Filter out old requests
            self.requests[key] = [
                request for request in self.requests[key]
                if current_time - request < timedelta(seconds=period)
            ]
            
        except Exception as e:
            logger.error("Error cleaning old requests", exc_info=True)
    
    def _get_rate_limit_info(
        self,
        key: str,
        limit: RateLimit,
        current_requests: int
    ) -> RateLimitInfo:
        """Get rate limit information"""
        try:
            # Get oldest request
            oldest_request = min(
                self.requests[key],
                default=datetime.utcnow()
            )
            
            # Calculate reset time
            reset_time = oldest_request + timedelta(seconds=limit.period)
            
            return RateLimitInfo(
                remaining=max(0, limit.requests - current_requests),
                reset=reset_time,
                limit=limit.requests,
                burst=limit.burst
            )
            
        except Exception as e:
            logger.error("Error getting rate limit info", exc_info=True)
            return RateLimitInfo(
                remaining=0,
                reset=datetime.utcnow(),
                limit=0,
                burst=None
            )
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                self._cleanup()
            except Exception as e:
                logger.error("Error in cleanup loop", exc_info=True)
    
    def _cleanup(self):
        """Clean up old rate limit data"""
        try:
            # Get current time
            current_time = datetime.utcnow()
            
            # Clean up old requests
            for key in list(self.requests.keys()):
                with self.locks[key]:
                    # Get limit type
                    limit_type = 'default'
                    for type_key, limit in self.limits.items():
                        if key.startswith(type_key):
                            limit_type = type_key
                            break
                    
                    # Clean old requests
                    self._clean_old_requests(key, self.limits[limit_type].period)
                    
                    # Remove empty lists
                    if not self.requests[key]:
                        del self.requests[key]
                        del self.locks[key]
                        
        except Exception as e:
            logger.error("Error cleaning up rate limiter", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        try:
            stats = {
                'total_keys': len(self.requests),
                'limits': {}
            }
            
            # Get stats for each limit type
            for limit_type, limit in self.limits.items():
                stats['limits'][limit_type] = {
                    'requests': limit.requests,
                    'period': limit.period,
                    'burst': limit.burst,
                    'active_keys': len([
                        key for key in self.requests.keys()
                        if key.startswith(limit_type)
                    ])
                }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting rate limiter stats", exc_info=True)
            return {}
    
    def set_limit(
        self,
        limit_type: str,
        requests: int,
        period: int,
        burst: Optional[int] = None
    ):
        """Set rate limit configuration"""
        try:
            self.limits[limit_type] = RateLimit(
                requests=requests,
                period=period,
                burst=burst
            )
        except Exception as e:
            logger.error("Error setting rate limit", exc_info=True)
    
    def remove_limit(self, limit_type: str):
        """Remove rate limit configuration"""
        try:
            if limit_type in self.limits:
                del self.limits[limit_type]
        except Exception as e:
            logger.error("Error removing rate limit", exc_info=True)
    
    def get_all_limits(self) -> Dict[str, RateLimit]:
        """Get all rate limit configurations"""
        try:
            return self.limits.copy()
        except Exception as e:
            logger.error("Error getting all rate limits", exc_info=True)
            return {}
    
    def get_active_keys(self) -> List[str]:
        """Get all active rate limit keys"""
        try:
            return list(self.requests.keys())
        except Exception as e:
            logger.error("Error getting active keys", exc_info=True)
            return []
    
    def get_key_stats(self, key: str) -> Dict[str, Any]:
        """Get statistics for a specific key"""
        try:
            with self.locks[key]:
                return {
                    'requests': len(self.requests[key]),
                    'oldest_request': min(
                        self.requests[key],
                        default=datetime.utcnow()
                    ),
                    'newest_request': max(
                        self.requests[key],
                        default=datetime.utcnow()
                    )
                }
        except Exception as e:
            logger.error("Error getting key stats", exc_info=True)
            return {} 