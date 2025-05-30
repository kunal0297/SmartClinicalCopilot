"""
Database metrics module.
This module re-exports the PerformanceMetrics class from the monitoring package.
"""

from backend.monitoring.metrics import PerformanceMetrics

__all__ = ['PerformanceMetrics'] 