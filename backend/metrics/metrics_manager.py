from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Module-level Prometheus metrics (singletons)
llm_requests_total = Counter('llm_requests_total', 'Total number of LLM requests', ['model', 'endpoint'])
llm_request_duration = Histogram('llm_request_duration_seconds', 'Duration of LLM requests in seconds', ['model', 'endpoint'])
llm_tokens_used = Counter('llm_tokens_used_total', 'Total number of tokens used', ['model', 'endpoint'])
active_llm_connections = Gauge('active_llm_connections', 'Number of active LLM connections', ['model'])

class MetricsManager:
    def track_request(self, model: str, endpoint: str, duration: float, tokens: int):
        """Track an LLM request with its metrics."""
        try:
            llm_requests_total.labels(model=model, endpoint=endpoint).inc()
            llm_request_duration.labels(model=model, endpoint=endpoint).observe(duration)
            llm_tokens_used.labels(model=model, endpoint=endpoint).inc(tokens)
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")

    def increment_connections(self, model: str):
        """Increment the count of active connections for a model."""
        try:
            active_llm_connections.labels(model=model).inc()
        except Exception as e:
            logger.error(f"Error incrementing connection count: {str(e)}")

    def decrement_connections(self, model: str):
        """Decrement the count of active connections for a model."""
        try:
            active_llm_connections.labels(model=model).dec()
        except Exception as e:
            logger.error(f"Error decrementing connection count: {str(e)}")

    def get_metrics(self):
        """Get current metrics values."""
        try:
            return {
                'llm_requests_total': llm_requests_total.collect(),
                'llm_tokens_used': llm_tokens_used.collect(),
                'active_connections': active_llm_connections.collect()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return {} 