import psutil
import asyncio
import aiohttp
import prometheus_client
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from .metrics import (
    SystemMetrics,
    ServiceMetrics,
    PerformanceMetrics,
    SecurityMetrics,
    HealthMetrics
)

logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """System status data class"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    uptime: float
    load_average: List[float]
    timestamp: datetime

class SystemMonitor:
    """Advanced system monitoring with Prometheus metrics"""
    
    def __init__(self):
        # Initialize Prometheus metrics
        self.cpu_usage = prometheus_client.Gauge(
            'system_cpu_usage',
            'CPU usage percentage'
        )
        self.memory_usage = prometheus_client.Gauge(
            'system_memory_usage',
            'Memory usage percentage'
        )
        self.disk_usage = prometheus_client.Gauge(
            'system_disk_usage',
            'Disk usage percentage'
        )
        self.network_io = prometheus_client.Gauge(
            'system_network_io',
            'Network I/O bytes',
            ['direction']
        )
        self.process_count = prometheus_client.Gauge(
            'system_process_count',
            'Number of running processes'
        )
        self.uptime = prometheus_client.Gauge(
            'system_uptime',
            'System uptime in seconds'
        )
        self.load_average = prometheus_client.Gauge(
            'system_load_average',
            'System load average',
            ['interval']
        )
        
        # Initialize metrics storage
        self.metrics_history: List[SystemStatus] = []
        self.max_history_size = 1000
        
        # Initialize monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.is_running = False

    async def start_monitoring(self):
        """Start all monitoring tasks"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_service_health()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._monitor_security()),
            asyncio.create_task(self._cleanup_old_metrics())
        ]
        
        logger.info("System monitoring started")

    async def stop_monitoring(self):
        """Stop all monitoring tasks"""
        if not self.is_running:
            return
            
        self.is_running = False
        for task in self.monitoring_tasks:
            task.cancel()
            
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
        
        logger.info("System monitoring stopped")

    async def _monitor_system_metrics(self):
        """Monitor basic system metrics"""
        while self.is_running:
            try:
                # Get CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)
                
                # Get memory metrics
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.percent)
                
                # Get disk metrics
                disk = psutil.disk_usage('/')
                self.disk_usage.set(disk.percent)
                
                # Get network metrics
                net_io = psutil.net_io_counters()
                self.network_io.labels('bytes_sent').set(net_io.bytes_sent)
                self.network_io.labels('bytes_recv').set(net_io.bytes_recv)
                
                # Get process count
                process_count = len(psutil.pids())
                self.process_count.set(process_count)
                
                # Get uptime
                uptime = psutil.boot_time()
                self.uptime.set(uptime)
                
                # Get load average
                load_avg = psutil.getloadavg()
                for i, load in enumerate(load_avg):
                    self.load_average.labels(f'{i+1}m').set(load)
                
                # Store metrics
                status = SystemStatus(
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io={
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv
                    },
                    process_count=process_count,
                    uptime=uptime,
                    load_average=list(load_avg),
                    timestamp=datetime.utcnow()
                )
                
                self.metrics_history.append(status)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("Error monitoring system metrics", exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying

    async def _monitor_service_health(self):
        """Monitor health of critical services"""
        while self.is_running:
            try:
                services = [
                    "api",
                    "database",
                    "cache",
                    "queue",
                    "storage"
                ]
                
                for service in services:
                    health = await self._check_service_health(service)
                    ServiceMetrics.update_health(service, health)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Error monitoring service health", exc_info=True)
                await asyncio.sleep(5)

    async def _monitor_performance(self):
        """Monitor application performance metrics"""
        while self.is_running:
            try:
                # Monitor request latency
                PerformanceMetrics.update_latency()
                
                # Monitor throughput
                PerformanceMetrics.update_throughput()
                
                # Monitor error rates
                PerformanceMetrics.update_error_rates()
                
                # Monitor resource utilization
                PerformanceMetrics.update_resource_utilization()
                
                await asyncio.sleep(15)  # Update every 15 seconds
                
            except Exception as e:
                logger.error("Error monitoring performance", exc_info=True)
                await asyncio.sleep(5)

    async def _monitor_security(self):
        """Monitor security metrics"""
        while self.is_running:
            try:
                # Monitor failed login attempts
                SecurityMetrics.update_failed_logins()
                
                # Monitor suspicious activities
                SecurityMetrics.update_suspicious_activities()
                
                # Monitor API usage
                SecurityMetrics.update_api_usage()
                
                # Monitor access patterns
                SecurityMetrics.update_access_patterns()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("Error monitoring security", exc_info=True)
                await asyncio.sleep(5)

    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        while self.is_running:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error("Error cleaning up metrics", exc_info=True)
                await asyncio.sleep(300)

    async def _check_service_health(self, service: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{service}/health") as response:
                    if response.status == 200:
                        return await response.json()
                    return {"status": "unhealthy", "error": response.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_current_status(self) -> SystemStatus:
        """Get current system status"""
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]

    def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SystemStatus]:
        """Get historical metrics within a time range"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
            
        return [
            m for m in self.metrics_history
            if start_time <= m.timestamp <= end_time
        ]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        if not self.metrics_history:
            return {}
            
        current = self.metrics_history[-1]
        return {
            "cpu_usage": {
                "current": current.cpu_usage,
                "average": sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history),
                "max": max(m.cpu_usage for m in self.metrics_history)
            },
            "memory_usage": {
                "current": current.memory_usage,
                "average": sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history),
                "max": max(m.memory_usage for m in self.metrics_history)
            },
            "disk_usage": {
                "current": current.disk_usage,
                "average": sum(m.disk_usage for m in self.metrics_history) / len(self.metrics_history),
                "max": max(m.disk_usage for m in self.metrics_history)
            },
            "network_io": {
                "current": current.network_io,
                "total_sent": sum(m.network_io['bytes_sent'] for m in self.metrics_history),
                "total_recv": sum(m.network_io['bytes_recv'] for m in self.metrics_history)
            },
            "process_count": {
                "current": current.process_count,
                "average": sum(m.process_count for m in self.metrics_history) / len(self.metrics_history),
                "max": max(m.process_count for m in self.metrics_history)
            },
            "uptime": current.uptime,
            "load_average": {
                "current": current.load_average,
                "average": [
                    sum(m.load_average[i] for m in self.metrics_history) / len(self.metrics_history)
                    for i in range(3)
                ]
            },
            "timestamp": current.timestamp.isoformat()
        } 