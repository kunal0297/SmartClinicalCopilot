import logging
from typing import Dict, Any, List
from datetime import datetime
import json
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackSystem:
    def __init__(self, feedback_file: str = "feedback.json"):
        self.feedback_file = feedback_file
        self._ensure_feedback_file()

    def _ensure_feedback_file(self):
        """Ensure the feedback file exists."""
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump([], f)

    async def record_feedback(self, alert_id: str, rule_id: str, 
                            helpful: bool, comments: str = None) -> Dict[str, Any]:
        """Record feedback for an alert."""
        try:
            feedback = {
                "alert_id": alert_id,
                "rule_id": rule_id,
                "helpful": helpful,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            }

            # Read existing feedback
            with open(self.feedback_file, 'r') as f:
                feedback_list = json.load(f)

            # Add new feedback
            feedback_list.append(feedback)

            # Write back to file
            with open(self.feedback_file, 'w') as f:
                json.dump(feedback_list, f, indent=2)

            return feedback

        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            return None

    async def get_rule_feedback(self, rule_id: str) -> Dict[str, Any]:
        """Get feedback statistics for a rule."""
        try:
            with open(self.feedback_file, 'r') as f:
                feedback_list = json.load(f)

            # Filter feedback for this rule
            rule_feedback = [f for f in feedback_list if f["rule_id"] == rule_id]
            
            if not rule_feedback:
                return {
                    "rule_id": rule_id,
                    "total_feedback": 0,
                    "helpful_count": 0,
                    "helpful_percentage": 0
                }

            total = len(rule_feedback)
            helpful = sum(1 for f in rule_feedback if f["helpful"])

            return {
                "rule_id": rule_id,
                "total_feedback": total,
                "helpful_count": helpful,
                "helpful_percentage": (helpful / total) * 100 if total > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting rule feedback: {str(e)}")
            return None

    async def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent feedback entries."""
        try:
            with open(self.feedback_file, 'r') as f:
                feedback_list = json.load(f)

            # Sort by timestamp and get most recent
            sorted_feedback = sorted(
                feedback_list,
                key=lambda x: x["timestamp"],
                reverse=True
            )

            return sorted_feedback[:limit]

        except Exception as e:
            logger.error(f"Error getting recent feedback: {str(e)}")
            return [] 