import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from fhirclient import client
from .config import settings
from .rule_engine import RuleEngine
from .alert_suppression import AlertSuppressionEngine

logger = logging.getLogger(__name__)

class FHIRSubscriptionHandler:
    def __init__(self):
        self.fhir_client = client.FHIRClient(
            settings=client.FHIRClientSettings(
                base_url=settings.FHIR_BASE_URL,
                app_id=settings.FHIR_APP_ID,
                timeout=30,
                retry_count=3
            )
        )
        self.rule_engine = RuleEngine()
        self.alert_suppression = AlertSuppressionEngine()
        self.active_subscriptions = {}
        self.subscription_handlers = {}
        self.websocket = None
        self.is_running = False
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 5
        self.reconnect_attempts = 0
        self.processing_queue = asyncio.Queue()
        self.worker_tasks = []

    async def start(self):
        """Start the subscription handler with improved error handling"""
        try:
            self.is_running = True
            # Initialize subscriptions
            await self._initialize_subscriptions()
            
            # Start WebSocket listener
            await self._start_websocket_listener()
            
            # Start worker tasks
            self.worker_tasks = [
                asyncio.create_task(self._process_queue())
                for _ in range(settings.WORKER_COUNT)
            ]
            
            logger.info("FHIR subscription handler started successfully")
        except Exception as e:
            logger.error(f"Failed to start FHIR subscription handler: {str(e)}")
            await self.stop()
            raise

    async def _initialize_subscriptions(self):
        """Initialize FHIR subscriptions for different resource types with retry logic"""
        resource_types = [
            'Observation',
            'MedicationRequest',
            'Condition',
            'Procedure',
            'DiagnosticReport'
        ]

        for resource_type in resource_types:
            retry_count = 0
            while retry_count < 3:
                try:
                    subscription = await self._create_subscription(resource_type)
                    self.active_subscriptions[resource_type] = subscription
                    logger.info(f"Created subscription for {resource_type}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == 3:
                        logger.error(f"Failed to create subscription for {resource_type} after 3 attempts: {str(e)}")
                    else:
                        logger.warning(f"Retrying subscription creation for {resource_type}: {str(e)}")
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff

    async def _create_subscription(self, resource_type: str) -> Dict[str, Any]:
        """Create a FHIR subscription for a resource type with validation"""
        subscription = {
            "resourceType": "Subscription",
            "status": "active",
            "reason": f"Clinical decision support for {resource_type}",
            "criteria": f"{resource_type}?",
            "channel": {
                "type": "websocket",
                "endpoint": f"ws://{settings.SERVER_HOST}:{settings.SERVER_PORT}/fhir/ws",
                "payload": "application/fhir+json",
                "headers": {
                    "Authorization": f"Bearer {settings.FHIR_API_KEY}"
                }
            }
        }

        try:
            response = await self.fhir_client.create(subscription)
            if not response or 'id' not in response:
                raise ValueError("Invalid subscription response")
            return response
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            raise

    async def _start_websocket_listener(self):
        """Start WebSocket listener for FHIR notifications with reconnection logic"""
        while self.is_running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        f"ws://{settings.SERVER_HOST}:{settings.SERVER_PORT}/fhir/ws",
                        heartbeat=30,
                        timeout=60
                    ) as ws:
                        self.websocket = ws
                        self.reconnect_attempts = 0
                        logger.info("WebSocket connection established")
                        
                        async for msg in ws:
                            if not self.is_running:
                                break
                                
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.processing_queue.put(json.loads(msg.data))
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket error: {ws.exception()}")
                                break
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                logger.warning("WebSocket connection closed")
                                break
                                
            except Exception as e:
                logger.error(f"WebSocket connection error: {str(e)}")
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    self.reconnect_attempts += 1
                    delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
                    logger.info(f"Attempting to reconnect in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max reconnection attempts reached")
                    break

    async def _process_queue(self):
        """Process notifications from the queue with error handling"""
        while self.is_running:
            try:
                notification = await self.processing_queue.get()
                await self._handle_notification(notification)
                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing notification: {str(e)}")
                await asyncio.sleep(1)  # Prevent tight loop on errors

    async def _handle_notification(self, notification: Dict[str, Any]):
        """Handle a FHIR notification with improved error handling"""
        try:
            resource_type = notification.get('resourceType')
            if not resource_type:
                logger.warning("Received notification without resource type")
                return

            resource_id = notification.get('id')
            if not resource_id:
                logger.warning("Received notification without resource ID")
                return

            # Fetch the full resource with retry logic
            resource = await self._fetch_resource_with_retry(resource_type, resource_id)
            if not resource:
                return

            # Process the resource
            await self._process_resource(resource)

        except Exception as e:
            logger.error(f"Error handling notification: {str(e)}")

    async def _fetch_resource_with_retry(self, resource_type: str, resource_id: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fetch a FHIR resource with retry logic"""
        for attempt in range(max_retries):
            try:
                response = await self.fhir_client.read(f"{resource_type}/{resource_id}")
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch resource after {max_retries} attempts: {str(e)}")
                    return None
                logger.warning(f"Retrying resource fetch (attempt {attempt + 1}): {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _process_resource(self, resource: Dict[str, Any]):
        """Process a FHIR resource through the rule engine with improved error handling"""
        try:
            # Evaluate rules
            alerts = await self.rule_engine.evaluate_resource(resource)
            
            # Filter suppressed alerts
            filtered_alerts = []
            for alert in alerts:
                if not await self.alert_suppression.should_suppress_alert(alert):
                    filtered_alerts.append(alert)

            # Process non-suppressed alerts
            if filtered_alerts:
                await self._handle_alerts(filtered_alerts, resource)

        except Exception as e:
            logger.error(f"Error processing resource: {str(e)}")

    async def _handle_alerts(self, alerts: List[Dict[str, Any]], resource: Dict[str, Any]):
        """Handle generated alerts with improved error handling"""
        try:
            for alert in alerts:
                # Add resource context to alert
                alert['resource'] = {
                    'type': resource['resourceType'],
                    'id': resource['id'],
                    'timestamp': datetime.now().isoformat()
                }

                # Send alert to notification system
                await self._send_alert(alert)

        except Exception as e:
            logger.error(f"Error handling alerts: {str(e)}")

    async def _send_alert(self, alert: Dict[str, Any]):
        """Send an alert to the notification system with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Implement alert notification logic here
                # This could be sending to a message queue, webhook, etc.
                logger.info(f"Alert generated: {json.dumps(alert)}")
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send alert after {max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Retrying alert send (attempt {attempt + 1}): {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def stop(self):
        """Stop the subscription handler with proper cleanup"""
        try:
            self.is_running = False
            
            # Cancel worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Close WebSocket connection
            if self.websocket:
                await self.websocket.close()
            
            # Delete active subscriptions
            for resource_type, subscription in self.active_subscriptions.items():
                try:
                    await self.fhir_client.delete(f"Subscription/{subscription['id']}")
                    logger.info(f"Deleted subscription for {resource_type}")
                except Exception as e:
                    logger.error(f"Failed to delete subscription for {resource_type}: {str(e)}")

            logger.info("FHIR subscription handler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping FHIR subscription handler: {str(e)}")
            raise 