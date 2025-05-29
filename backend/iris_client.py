import os
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class IRISClient:
    def __init__(self):
        self.iris_host = os.getenv("IRIS_HOST", "localhost")
        self.iris_port = os.getenv("IRIS_PORT", "52773")
        self.iris_namespace = os.getenv("IRIS_NAMESPACE", "USER")
        self.iris_username = os.getenv("IRIS_USERNAME", "_SYSTEM")
        self.iris_password = os.getenv("IRIS_PASSWORD", "SYS")
        self.base_url = f"http://{self.iris_host}:{self.iris_port}/api/atlas/v1"
        self.session = None

    async def _ensure_session(self):
        """Ensure we have an active session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(self.iris_username, self.iris_password)
            )

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive patient data from IRIS"""
        try:
            await self._ensure_session()
            
            # Fetch basic patient information
            patient_info = await self._fetch_patient_info(patient_id)
            
            # Fetch medical history
            medical_history = await self._fetch_medical_history(patient_id)
            
            # Fetch current medications
            medications = await self._fetch_medications(patient_id)
            
            # Fetch lab results
            lab_results = await self._fetch_lab_results(patient_id)
            
            # Fetch diagnoses
            diagnoses = await self._fetch_diagnoses(patient_id)
            
            return {
                "id": patient_id,
                "age": patient_info.get("age"),
                "gender": patient_info.get("gender"),
                "medical_history": medical_history,
                "medications": medications,
                "lab_results": lab_results,
                "diagnoses": diagnoses,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching patient data: {str(e)}")
            raise

    async def _fetch_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """Fetch basic patient information"""
        try:
            url = f"{self.base_url}/patients/{patient_id}"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching patient info: {str(e)}")
            return {}

    async def _fetch_medical_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """Fetch patient's medical history"""
        try:
            url = f"{self.base_url}/patients/{patient_id}/medical-history"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching medical history: {str(e)}")
            return []

    async def _fetch_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Fetch patient's current medications"""
        try:
            url = f"{self.base_url}/patients/{patient_id}/medications"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching medications: {str(e)}")
            return []

    async def _fetch_lab_results(self, patient_id: str) -> List[Dict[str, Any]]:
        """Fetch patient's lab results"""
        try:
            url = f"{self.base_url}/patients/{patient_id}/lab-results"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching lab results: {str(e)}")
            return []

    async def _fetch_diagnoses(self, patient_id: str) -> List[Dict[str, Any]]:
        """Fetch patient's diagnoses"""
        try:
            url = f"{self.base_url}/patients/{patient_id}/diagnoses"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching diagnoses: {str(e)}")
            return []

    async def store_patient_summary(self, patient_id: str, summary: str) -> bool:
        """Store the generated patient summary in IRIS"""
        try:
            await self._ensure_session()
            
            url = f"{self.base_url}/patients/{patient_id}/summaries"
            data = {
                "summary": summary,
                "generated_at": datetime.now().isoformat(),
                "type": "ai_generated"
            }
            
            async with self.session.post(url, json=data) as response:
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Error storing patient summary: {str(e)}")
            return False

    async def get_patient_summaries(self, patient_id: str) -> List[Dict[str, Any]]:
        """Retrieve all stored summaries for a patient"""
        try:
            await self._ensure_session()
            
            url = f"{self.base_url}/patients/{patient_id}/summaries"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error fetching patient summaries: {str(e)}")
            return [] 