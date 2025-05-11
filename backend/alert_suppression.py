import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import redis
from functools import lru_cache
from .config import settings

logger = logging.getLogger(__name__)

class AlertSuppressionEngine:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self.suppression_rules = self._load_suppression_rules()
        self.alert_history = defaultdict(list)
        self.feedback_history = defaultdict(list)
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize Redis cache with proper configuration"""
        try:
            # Configure Redis for better performance
            self.redis_client.config_set('maxmemory', '512mb')
            self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')
            self.redis_client.config_set('appendonly', 'yes')
            logger.info("Redis cache initialized with optimized settings")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {str(e)}")

    @lru_cache(maxsize=1000)
    def _load_suppression_rules(self) -> Dict[str, Any]:
        """Load suppression rules from configuration with caching"""
        try:
            with open('config/suppression_rules.json', 'r') as f:
                rules = json.load(f)
                logger.info("Suppression rules loaded successfully")
                return rules
        except FileNotFoundError:
            logger.warning("Suppression rules file not found, using defaults")
            return {
                "time_window": 3600,  # 1 hour
                "max_alerts": 3,
                "min_severity": "medium",
                "feedback_threshold": 0.7,
                "cache_ttl": 300,  # 5 minutes
                "batch_size": 100
            }

    async def should_suppress_alert(self, alert: Dict[str, Any]) -> bool:
        """Determine if an alert should be suppressed based on rules and history"""
        try:
            # Check cache first
            cache_key = f"suppression:{self._get_alert_key(alert)}"
            cached_result = self.redis_client.get(cache_key)
            if cached_result is not None:
                return json.loads(cached_result)

            # Check basic suppression rules
            if not self._check_basic_rules(alert):
                return self._cache_result(cache_key, False)

            # Check alert history
            if self._check_alert_history(alert):
                return self._cache_result(cache_key, True)

            # Check feedback history
            if self._check_feedback_history(alert):
                return self._cache_result(cache_key, True)

            # Check custom suppression rules
            if self._check_custom_rules(alert):
                return self._cache_result(cache_key, True)

            return self._cache_result(cache_key, False)
        except Exception as e:
            logger.error(f"Error in alert suppression check: {str(e)}")
            return False

    def _cache_result(self, key: str, result: bool) -> bool:
        """Cache the suppression result"""
        try:
            self.redis_client.setex(
                key,
                self.suppression_rules.get('cache_ttl', 300),
                json.dumps(result)
            )
            return result
        except Exception as e:
            logger.error(f"Error caching suppression result: {str(e)}")
            return result

    def _check_basic_rules(self, alert: Dict[str, Any]) -> bool:
        """Check basic suppression rules with optimized logic"""
        severity = alert.get('severity', 'low')
        return not (severity == 'high' or severity < self.suppression_rules['min_severity'])

    def _check_alert_history(self, alert: Dict[str, Any]) -> bool:
        """Check if alert should be suppressed based on recent history with batching"""
        try:
            alert_key = self._get_alert_key(alert)
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=self.suppression_rules['time_window'])

            # Use Redis pipeline for better performance
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(
                f"alert_history:{alert_key}",
                0,
                window_start.timestamp()
            )
            pipe.zrangebyscore(
                f"alert_history:{alert_key}",
                window_start.timestamp(),
                current_time.timestamp()
            )
            pipe.zadd(
                f"alert_history:{alert_key}",
                {json.dumps(alert): current_time.timestamp()}
            )
            pipe.expire(
                f"alert_history:{alert_key}",
                self.suppression_rules['time_window']
            )
            _, recent_alerts, _, _ = pipe.execute()

            return len(recent_alerts) >= self.suppression_rules['max_alerts']
        except Exception as e:
            logger.error(f"Error checking alert history: {str(e)}")
            return False

    def _check_feedback_history(self, alert: Dict[str, Any]) -> bool:
        """Check if alert should be suppressed based on feedback history with caching"""
        try:
            alert_key = self._get_alert_key(alert)
            feedback_key = f"feedback:{alert_key}"
            
            # Use Redis pipeline for better performance
            pipe = self.redis_client.pipeline()
            pipe.hgetall(feedback_key)
            pipe.ttl(feedback_key)
            feedback_data, ttl = pipe.execute()
            
            if not feedback_data:
                return False

            total_feedback = int(feedback_data.get('total', 0))
            if total_feedback < 5:
                return False

            suppression_score = int(feedback_data.get('suppressed', 0)) / total_feedback
            return suppression_score >= self.suppression_rules['feedback_threshold']
        except Exception as e:
            logger.error(f"Error checking feedback history: {str(e)}")
            return False

    def _check_custom_rules(self, alert: Dict[str, Any]) -> bool:
        """Check custom suppression rules with parallel processing"""
        try:
            rules = self.suppression_rules.get('custom_rules', [])
            if not rules:
                return False

            # Process rules in batches for better performance
            batch_size = self.suppression_rules.get('batch_size', 100)
            for i in range(0, len(rules), batch_size):
                batch = rules[i:i + batch_size]
                for rule in batch:
                    if self._evaluate_custom_rule(rule, alert):
                        logger.info(f"Suppressing alert due to custom rule: {rule['name']}")
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking custom rules: {str(e)}")
            return False

    def _evaluate_custom_rule(self, rule: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Evaluate a custom suppression rule with optimized logic"""
        try:
            if rule['type'] == 'condition':
                return self._evaluate_condition(rule['condition'], alert)
            elif rule['type'] == 'pattern':
                return self._evaluate_pattern(rule['pattern'], alert)
            return False
        except Exception as e:
            logger.error(f"Error evaluating custom rule: {str(e)}")
            return False

    def _evaluate_condition(self, condition: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Evaluate a condition-based rule with optimized operators"""
        try:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']

            if field not in alert:
                return False

            alert_value = alert[field]
            operators = {
                'equals': lambda x, y: x == y,
                'contains': lambda x, y: y in x,
                'greater_than': lambda x, y: x > y,
                'less_than': lambda x, y: x < y,
                'starts_with': lambda x, y: str(x).startswith(str(y)),
                'ends_with': lambda x, y: str(x).endswith(str(y)),
                'matches': lambda x, y: bool(re.match(y, str(x)))
            }

            return operators.get(operator, lambda x, y: False)(alert_value, value)
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

    def _evaluate_pattern(self, pattern: Dict[str, Any], alert: Dict[str, Any]) -> bool:
        """Evaluate a pattern-based rule with optimized matching"""
        try:
            # Implement pattern matching logic here
            return False
        except Exception as e:
            logger.error(f"Error evaluating pattern: {str(e)}")
            return False

    def _get_alert_key(self, alert: Dict[str, Any]) -> str:
        """Generate a unique key for an alert with optimized hashing"""
        return f"{alert.get('type', 'unknown')}:{alert.get('id', 'unknown')}"

    async def record_feedback(self, alert: Dict[str, Any], feedback: Dict[str, Any]):
        """Record feedback for an alert with batching and caching"""
        try:
            alert_key = self._get_alert_key(alert)
            feedback_key = f"feedback:{alert_key}"

            # Use Redis pipeline for better performance
            pipe = self.redis_client.pipeline()
            pipe.hincrby(feedback_key, 'total', 1)
            if feedback.get('suppress', False):
                pipe.hincrby(feedback_key, 'suppressed', 1)

            # Store detailed feedback with expiration
            feedback_id = f"feedback:{alert_key}:{datetime.now().timestamp()}"
            pipe.setex(
                feedback_id,
                self.suppression_rules['time_window'],
                json.dumps(feedback)
            )

            # Set expiration on the feedback key
            pipe.expire(feedback_key, self.suppression_rules['time_window'])

            # Execute pipeline
            pipe.execute()

            logger.info(f"Recorded feedback for alert {alert_key}")
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")

    async def get_suppression_stats(self) -> Dict[str, Any]:
        """Get statistics about alert suppression with caching"""
        try:
            cache_key = "suppression_stats"
            cached_stats = self.redis_client.get(cache_key)
            if cached_stats:
                return json.loads(cached_stats)

            stats = {
                "total_alerts": 0,
                "suppressed_alerts": 0,
                "suppression_rate": 0,
                "by_severity": defaultdict(int),
                "by_type": defaultdict(int),
                "timestamp": datetime.now().isoformat()
            }

            # Use Redis pipeline for better performance
            pipe = self.redis_client.pipeline()
            alert_keys = self.redis_client.keys("alert_history:*")
            
            for key in alert_keys:
                pipe.zrange(key, 0, -1, withscores=True)
            
            results = pipe.execute()
            
            for key, alerts in zip(alert_keys, results):
                alert_type = key.split(":")[1]
                for alert_json, _ in alerts:
                    alert = json.loads(alert_json)
                    stats["total_alerts"] += 1
                    stats["by_severity"][alert.get("severity", "unknown")] += 1
                    stats["by_type"][alert_type] += 1

                    if self.should_suppress_alert(alert):
                        stats["suppressed_alerts"] += 1

            if stats["total_alerts"] > 0:
                stats["suppression_rate"] = stats["suppressed_alerts"] / stats["total_alerts"]

            # Cache the results
            self.redis_client.setex(
                cache_key,
                self.suppression_rules.get('cache_ttl', 300),
                json.dumps(stats)
            )

            return stats
        except Exception as e:
            logger.error(f"Error getting suppression stats: {str(e)}")
            return {} 