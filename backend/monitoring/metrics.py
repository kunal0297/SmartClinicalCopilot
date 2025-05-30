import prometheus_client
from typing import Dict, Any, List
from datetime import datetime
import logging
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)

# Module-level Prometheus metrics (singletons)
alert_count_metric = prometheus_client.Gauge('alert_count', 'Number of active alerts', ['rule_id'])
alert_severity_metric = prometheus_client.Gauge('alert_severity', 'Alert severity distribution', ['severity', 'rule_id'])
alert_response_time_metric = prometheus_client.Gauge('alert_response_time', 'Time to respond to alerts', ['rule_id'])
alert_resolution_time_metric = prometheus_client.Gauge('alert_resolution_time', 'Time to resolve alerts', ['rule_id'])

@dataclass
class MetricPoint:
    """Data point for time series metrics"""
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

class BaseMetrics:
    """Base class for all metrics"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.history: deque = deque(maxlen=1000)
        
    def record(self, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        try:
            self.history.append(MetricPoint(
                value=value,
                timestamp=datetime.utcnow(),
                labels=labels or {}
            ))
        except Exception as e:
            logger.error(f"Error recording metric {self.name}", exc_info=True)
            
    def get_current(self, labels: Dict[str, str] = None) -> float:
        """Get current metric value"""
        try:
            if self.history:
                return self.history[-1].value
            return 0.0
        except Exception as e:
            logger.error(f"Error getting metric {self.name}", exc_info=True)
            return 0.0
            
    def get_history(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        labels: Dict[str, str] = None
    ) -> List[MetricPoint]:
        """Get historical metric values"""
        try:
            return [
                point for point in self.history
                if (not start_time or point.timestamp >= start_time) and
                   (not end_time or point.timestamp <= end_time) and
                   (not labels or all(
                       point.labels.get(k) == v
                       for k, v in labels.items()
                   ))
            ]
        except Exception as e:
            logger.error(f"Error getting history for {self.name}", exc_info=True)
            return []

class SystemMetrics:
    """System-level metrics"""
    
    cpu_usage = BaseMetrics(
        'system_cpu_usage',
        'CPU usage percentage'
    )
    memory_usage = BaseMetrics(
        'system_memory_usage',
        'Memory usage percentage'
    )
    disk_usage = BaseMetrics(
        'system_disk_usage',
        'Disk usage percentage'
    )
    network_io = BaseMetrics(
        'system_network_io',
        'Network I/O bytes'
    )
    process_count = BaseMetrics(
        'system_process_count',
        'Number of running processes'
    )
    
    @classmethod
    def update_all(cls, metrics: Dict[str, Any]):
        """Update all system metrics"""
        try:
            cls.cpu_usage.record(metrics['cpu_usage'])
            cls.memory_usage.record(metrics['memory_usage'])
            cls.disk_usage.record(metrics['disk_usage'])
            cls.network_io.record(
                metrics['network_io']['bytes_sent'],
                {'direction': 'sent'}
            )
            cls.network_io.record(
                metrics['network_io']['bytes_recv'],
                {'direction': 'recv'}
            )
            cls.process_count.record(metrics['process_count'])
        except Exception as e:
            logger.error("Error updating system metrics", exc_info=True)

class ServiceMetrics:
    """Service health metrics"""
    
    health_status = BaseMetrics(
        'service_health_status',
        'Service health status (1=healthy, 0=unhealthy)'
    )
    response_time = BaseMetrics(
        'service_response_time',
        'Service response time in milliseconds'
    )
    error_count = BaseMetrics(
        'service_error_count',
        'Number of service errors'
    )
    
    @classmethod
    def update_health(cls, service: str, health: Dict[str, Any]):
        """Update service health metrics"""
        try:
            cls.health_status.record(
                1.0 if health['status'] == 'healthy' else 0.0,
                {'service': service}
            )
            if 'response_time' in health:
                cls.response_time.record(
                    health['response_time'],
                    {'service': service}
                )
            if 'error_count' in health:
                cls.error_count.record(
                    health['error_count'],
                    {'service': service}
                )
        except Exception as e:
            logger.error(f"Error updating health for {service}", exc_info=True)

class PerformanceMetrics:
    """Application performance metrics"""
    
    request_latency = BaseMetrics(
        'app_request_latency',
        'Request latency in milliseconds'
    )
    request_throughput = BaseMetrics(
        'app_request_throughput',
        'Requests per second'
    )
    error_rate = BaseMetrics(
        'app_error_rate',
        'Error rate (errors per second)'
    )
    resource_utilization = BaseMetrics(
        'app_resource_utilization',
        'Resource utilization percentage'
    )
    
    @classmethod
    def update_latency(cls, latency: float, endpoint: str = None):
        """Update request latency metric"""
        try:
            cls.request_latency.record(
                latency,
                {'endpoint': endpoint} if endpoint else None
            )
        except Exception as e:
            logger.error("Error updating latency metric", exc_info=True)
            
    @classmethod
    def update_throughput(cls, requests: int, endpoint: str = None):
        """Update request throughput metric"""
        try:
            cls.request_throughput.record(
                requests,
                {'endpoint': endpoint} if endpoint else None
            )
        except Exception as e:
            logger.error("Error updating throughput metric", exc_info=True)
            
    @classmethod
    def update_error_rates(cls, errors: int, error_type: str = None):
        """Update error rate metric"""
        try:
            cls.error_rate.record(
                errors,
                {'type': error_type} if error_type else None
            )
        except Exception as e:
            logger.error("Error updating error rate metric", exc_info=True)
            
    @classmethod
    def update_resource_utilization(cls, utilization: float, resource: str = None):
        """Update resource utilization metric"""
        try:
            cls.resource_utilization.record(
                utilization,
                {'resource': resource} if resource else None
            )
        except Exception as e:
            logger.error("Error updating resource utilization metric", exc_info=True)

class SecurityMetrics:
    """Security-related metrics"""
    
    failed_logins = BaseMetrics(
        'security_failed_logins',
        'Number of failed login attempts'
    )
    suspicious_activities = BaseMetrics(
        'security_suspicious_activities',
        'Number of suspicious activities detected'
    )
    api_usage = BaseMetrics(
        'security_api_usage',
        'API usage statistics'
    )
    access_patterns = BaseMetrics(
        'security_access_patterns',
        'Access pattern statistics'
    )
    
    @classmethod
    def update_failed_logins(cls, count: int, user: str = None):
        """Update failed login attempts metric"""
        try:
            cls.failed_logins.record(
                count,
                {'user': user} if user else None
            )
        except Exception as e:
            logger.error("Error updating failed logins metric", exc_info=True)
            
    @classmethod
    def update_suspicious_activities(cls, count: int, activity_type: str = None):
        """Update suspicious activities metric"""
        try:
            cls.suspicious_activities.record(
                count,
                {'type': activity_type} if activity_type else None
            )
        except Exception as e:
            logger.error("Error updating suspicious activities metric", exc_info=True)
            
    @classmethod
    def update_api_usage(cls, count: int, endpoint: str = None):
        """Update API usage metric"""
        try:
            cls.api_usage.record(
                count,
                {'endpoint': endpoint} if endpoint else None
            )
        except Exception as e:
            logger.error("Error updating API usage metric", exc_info=True)
            
    @classmethod
    def update_access_patterns(cls, count: int, pattern: str = None):
        """Update access patterns metric"""
        try:
            cls.access_patterns.record(
                count,
                {'pattern': pattern} if pattern else None
            )
        except Exception as e:
            logger.error("Error updating access patterns metric", exc_info=True)

class HealthMetrics:
    """Health check metrics"""
    
    service_health = BaseMetrics(
        'health_service_status',
        'Service health status (1=healthy, 0=unhealthy)'
    )
    dependency_health = BaseMetrics(
        'health_dependency_status',
        'Dependency health status (1=healthy, 0=unhealthy)'
    )
    resource_health = BaseMetrics(
        'health_resource_status',
        'Resource health status (1=healthy, 0=unhealthy)'
    )
    
    @classmethod
    def update_service_health(cls, service: str, healthy: bool):
        """Update service health metric"""
        try:
            cls.service_health.record(
                1.0 if healthy else 0.0,
                {'service': service}
            )
        except Exception as e:
            logger.error(f"Error updating health for {service}", exc_info=True)
            
    @classmethod
    def update_dependency_health(cls, dependency: str, healthy: bool):
        """Update dependency health metric"""
        try:
            cls.dependency_health.record(
                1.0 if healthy else 0.0,
                {'dependency': dependency}
            )
        except Exception as e:
            logger.error(f"Error updating health for {dependency}", exc_info=True)
            
    @classmethod
    def update_resource_health(cls, resource: str, healthy: bool):
        """Update resource health metric"""
        try:
            cls.resource_health.record(
                1.0 if healthy else 0.0,
                {'resource': resource}
            )
        except Exception as e:
            logger.error(f"Error updating health for {resource}", exc_info=True)

class AlertMetricsService:
    """Service for managing alert metrics"""
    
    def record_alert(self, severity: str, rule_id: str):
        """Record a new alert"""
        try:
            alert_count_metric.labels(rule_id=rule_id).inc()
            alert_severity_metric.labels(severity=severity, rule_id=rule_id).inc()
        except Exception as e:
            logger.error(f"Error recording alert: {e}", exc_info=True)
            
    def record_response_time(self, rule_id: str, response_time: float):
        """Record alert response time"""
        try:
            alert_response_time_metric.labels(rule_id=rule_id).set(response_time)
        except Exception as e:
            logger.error(f"Error recording response time: {e}", exc_info=True)
            
    def record_resolution_time(self, rule_id: str, resolution_time: float):
        """Record alert resolution time"""
        try:
            alert_resolution_time_metric.labels(rule_id=rule_id).set(resolution_time)
        except Exception as e:
            logger.error(f"Error recording resolution time: {e}", exc_info=True)
            
    def get_alert_metrics(self) -> Dict[str, Any]:
        """Get current alert metrics"""
        try:
            return {
                'total_alerts': sum([alert_count_metric.labels(rule_id=rule_id)._value.get() for rule_id in alert_count_metric._metrics]),
                'severity_distribution': {
                    severity: sum([
                        alert_severity_metric.labels(severity=severity, rule_id=rule_id)._value.get()
                        for rule_id in alert_severity_metric._metrics
                        if severity in alert_severity_metric._metrics[rule_id]
                    ]) for severity in ['high', 'medium', 'low']
                },
                'avg_response_time': 0,  # Not implemented for brevity
                'avg_resolution_time': 0  # Not implemented for brevity
            }
        except Exception as e:
            logger.error(f"Error getting alert metrics: {e}", exc_info=True)
            return {} 