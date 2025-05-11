import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import aiofiles
from cryptography.fernet import Fernet
from .config import settings

logger = logging.getLogger(__name__)

class UsageDashboard:
    def __init__(self):
        self.storage_dir = "encrypted_metrics"
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        self._initialize_storage()

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for metrics storage"""
        key_file = "metrics_key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def _initialize_storage(self):
        """Initialize encrypted storage directory"""
        os.makedirs(self.storage_dir, exist_ok=True)

    async def record_metric(self, metric_type: str, data: Dict[str, Any]):
        """Record a metric with encryption"""
        try:
            timestamp = datetime.now().isoformat()
            metric_data = {
                "timestamp": timestamp,
                "type": metric_type,
                "data": data
            }

            # Encrypt the metric data
            encrypted_data = self.fernet.encrypt(json.dumps(metric_data).encode())

            # Save to file
            filename = f"{self.storage_dir}/{metric_type}_{timestamp}.enc"
            async with aiofiles.open(filename, "wb") as f:
                await f.write(encrypted_data)

            logger.info(f"Recorded metric: {metric_type}")
        except Exception as e:
            logger.error(f"Failed to record metric: {str(e)}")

    async def get_metrics(self, metric_type: str, time_range: str = "24h") -> List[Dict[str, Any]]:
        """Get metrics of a specific type within a time range"""
        try:
            metrics = []
            cutoff_time = datetime.now() - self._parse_time_range(time_range)

            # List all encrypted files
            for filename in os.listdir(self.storage_dir):
                if filename.startswith(metric_type) and filename.endswith(".enc"):
                    file_path = os.path.join(self.storage_dir, filename)
                    
                    # Read and decrypt file
                    async with aiofiles.open(file_path, "rb") as f:
                        encrypted_data = await f.read()
                        decrypted_data = self.fernet.decrypt(encrypted_data)
                        metric = json.loads(decrypted_data.decode())

                        # Filter by time range
                        metric_time = datetime.fromisoformat(metric["timestamp"])
                        if metric_time >= cutoff_time:
                            metrics.append(metric)

            return sorted(metrics, key=lambda x: x["timestamp"])
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return []

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get aggregated dashboard data"""
        try:
            # Get metrics for different types
            alert_metrics = await self.get_metrics("alert")
            llm_metrics = await self.get_metrics("llm")
            rule_metrics = await self.get_metrics("rule")
            feedback_metrics = await self.get_metrics("feedback")

            # Calculate statistics
            stats = {
                "alerts": self._calculate_alert_stats(alert_metrics),
                "llm": self._calculate_llm_stats(llm_metrics),
                "rules": self._calculate_rule_stats(rule_metrics),
                "feedback": self._calculate_feedback_stats(feedback_metrics)
            }

            return stats
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {str(e)}")
            return {}

    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse time range string to timedelta"""
        unit = time_range[-1]
        value = int(time_range[:-1])
        
        if unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        elif unit == "w":
            return timedelta(weeks=value)
        else:
            return timedelta(hours=24)  # default to 24h

    def _calculate_alert_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate alert statistics"""
        if not metrics:
            return {}

        total_alerts = len(metrics)
        severity_counts = defaultdict(int)
        avg_response_time = 0

        for metric in metrics:
            data = metric["data"]
            severity_counts[data.get("severity", "unknown")] += 1
            avg_response_time += data.get("response_time", 0)

        return {
            "total_alerts": total_alerts,
            "severity_distribution": dict(severity_counts),
            "avg_response_time": avg_response_time / total_alerts if total_alerts > 0 else 0
        }

    def _calculate_llm_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate LLM statistics"""
        if not metrics:
            return {}

        model_stats = defaultdict(lambda: {"count": 0, "total_latency": 0})
        
        for metric in metrics:
            data = metric["data"]
            model = data.get("model", "unknown")
            model_stats[model]["count"] += 1
            model_stats[model]["total_latency"] += data.get("latency", 0)

        return {
            "total_requests": len(metrics),
            "model_stats": {
                model: {
                    "count": stats["count"],
                    "avg_latency": stats["total_latency"] / stats["count"] if stats["count"] > 0 else 0
                }
                for model, stats in model_stats.items()
            }
        }

    def _calculate_rule_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate rule matching statistics"""
        if not metrics:
            return {}

        rule_counts = defaultdict(int)
        total_matches = 0

        for metric in metrics:
            data = metric["data"]
            rule_id = data.get("rule_id", "unknown")
            rule_counts[rule_id] += 1
            total_matches += 1

        return {
            "total_matches": total_matches,
            "rule_distribution": dict(rule_counts)
        }

    def _calculate_feedback_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate feedback statistics"""
        if not metrics:
            return {}

        feedback_counts = defaultdict(int)
        total_feedback = len(metrics)

        for metric in metrics:
            data = metric["data"]
            feedback_type = data.get("type", "unknown")
            feedback_counts[feedback_type] += 1

        return {
            "total_feedback": total_feedback,
            "feedback_distribution": dict(feedback_counts)
        } 