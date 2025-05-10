from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from .models import AlertMetrics, RuleMatch, AlertOverride

logger = logging.getLogger(__name__)

class AlertMetrics:
    def __init__(self):
        self.metrics_cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(minutes=5)

    def log_rule_matches(self, patient_id: str, rule_matches: List[RuleMatch], db: Session):
        """Log rule matches and update metrics"""
        try:
            for match in rule_matches:
                # Update or create metrics record
                metrics = db.query(AlertMetrics).filter_by(
                    patient_id=patient_id,
                    rule_id=match.rule_id
                ).first()
                
                if not metrics:
                    metrics = AlertMetrics(
                        patient_id=patient_id,
                        rule_id=match.rule_id,
                        alert_count=0,
                        override_count=0
                    )
                    db.add(metrics)
                
                # Update metrics
                metrics.alert_count += 1
                metrics.last_alert_at = datetime.utcnow()
                
                # Invalidate cache
                self._invalidate_cache(patient_id, match.rule_id)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging rule matches: {str(e)}")
            db.rollback()
            raise

    def log_override(self, alert_id: str, override_reason: str, db: Session):
        """Log alert override and update metrics"""
        try:
            # Get the alert
            alert = db.query(Alert).get(alert_id)
            if not alert:
                raise ValueError(f"Alert not found: {alert_id}")
            
            # Create override record
            override = AlertOverride(
                alert_id=alert_id,
                override_reason=override_reason,
                timestamp=datetime.utcnow()
            )
            db.add(override)
            
            # Update metrics
            metrics = db.query(AlertMetrics).filter_by(
                patient_id=alert.patient_id,
                rule_id=alert.rule_id
            ).first()
            
            if metrics:
                metrics.override_count += 1
                metrics.last_override_at = datetime.utcnow()
                
                # Invalidate cache
                self._invalidate_cache(alert.patient_id, alert.rule_id)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging alert override: {str(e)}")
            db.rollback()
            raise

    def get_metrics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get alert metrics and statistics"""
        try:
            # Check cache first
            cache_key = f"metrics_{start_date}_{end_date}"
            if cache_key in self.metrics_cache:
                cached_data, timestamp = self.metrics_cache[cache_key]
                if datetime.utcnow() - timestamp < self.cache_ttl:
                    return cached_data
            
            # Query metrics
            query = db.query(AlertMetrics)
            
            if start_date:
                query = query.filter(AlertMetrics.last_alert_at >= start_date)
            if end_date:
                query = query.filter(AlertMetrics.last_alert_at <= end_date)
            
            metrics = query.all()
            
            # Calculate statistics
            total_alerts = sum(m.alert_count for m in metrics)
            total_overrides = sum(m.override_count for m in metrics)
            override_rate = total_overrides / total_alerts if total_alerts > 0 else 0
            
            # Get top rules by alert count
            top_rules = sorted(
                metrics,
                key=lambda m: m.alert_count,
                reverse=True
            )[:10]
            
            # Compile results
            results = {
                "total_alerts": total_alerts,
                "total_overrides": total_overrides,
                "override_rate": override_rate,
                "top_rules": [
                    {
                        "rule_id": m.rule_id,
                        "alert_count": m.alert_count,
                        "override_count": m.override_count,
                        "override_rate": m.override_count / m.alert_count if m.alert_count > 0 else 0
                    }
                    for m in top_rules
                ],
                "time_period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
            # Cache results
            self.metrics_cache[cache_key] = (results, datetime.utcnow())
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise

    def get_patient_metrics(self, patient_id: str, db: Session) -> Dict[str, Any]:
        """Get metrics for a specific patient"""
        try:
            metrics = db.query(AlertMetrics).filter_by(patient_id=patient_id).all()
            
            return {
                "patient_id": patient_id,
                "total_alerts": sum(m.alert_count for m in metrics),
                "total_overrides": sum(m.override_count for m in metrics),
                "rules": [
                    {
                        "rule_id": m.rule_id,
                        "alert_count": m.alert_count,
                        "override_count": m.override_count,
                        "last_alert": m.last_alert_at.isoformat() if m.last_alert_at else None,
                        "last_override": m.last_override_at.isoformat() if m.last_override_at else None
                    }
                    for m in metrics
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting patient metrics: {str(e)}")
            raise

    def _invalidate_cache(self, patient_id: str, rule_id: int):
        """Invalidate metrics cache for a patient and rule"""
        keys_to_remove = []
        for key in self.metrics_cache:
            if f"metrics_{patient_id}_{rule_id}" in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.metrics_cache[key] 