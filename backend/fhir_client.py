import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from cachetools import TTLCache
from fhirclient import client
from fhirclient.models import patient, observation, medicationrequest, condition
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIRClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("FHIR_SERVER_URL", "http://localhost:52773/csp/healthshare/fhir/r4")
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5-minute cache
        self.smart = client.FHIRClient(settings={
            'app_id': 'smart_clinical_copilot',
            'api_base': self.base_url
        })
        self.session = None
        # Add authentication headers for IRIS
        self.auth_header = {
            'Authorization': 'Basic ' + base64.b64encode(b'SuperUser:AeQV@17463').decode('utf-8')
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.auth_header)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data with all related resources."""
        cache_key = f"patient_{patient_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Get patient basic info
            patient_data = await self._fetch_resource('Patient', patient_id)
            if not patient_data:
                return None

            # Get related resources
            observations = await self._fetch_observations(patient_id)
            medications = await self._fetch_medications(patient_id)
            conditions = await self._fetch_conditions(patient_id)

            # Process and normalize the data
            processed_data = self._process_patient_data(
                patient_data,
                observations,
                medications,
                conditions
            )

            # Cache the result
            self.cache[cache_key] = processed_data
            return processed_data

        except Exception as e:
            logger.error(f"Error fetching patient data: {str(e)}")
            return None

    def _process_patient_data(self, patient_data: Dict, observations: List[Dict],
                            medications: List[Dict], conditions: List[Dict]) -> Dict[str, Any]:
        """Process and normalize FHIR data into a consistent format."""
        processed = {
            "id": patient_data.get("id"),
            "name": self._get_patient_name(patient_data),
            "gender": patient_data.get("gender"),
            "birthDate": patient_data.get("birthDate"),
            "conditions": {
                "observations": self._process_observations(observations),
                "medications": self._process_medications(medications),
                "conditions": self._process_conditions(conditions)
            }
        }
        return processed

    def _get_patient_name(self, patient_data: Dict) -> List[Dict[str, str]]:
        """Extract patient name from FHIR data."""
        names = []
        for name in patient_data.get("name", []):
            if "text" in name:
                names.append({"text": name["text"]})
            elif "given" in name and "family" in name:
                given = " ".join(name["given"])
                names.append({"text": f"{given} {name['family']}"})
        return names

    def _process_observations(self, observations: List[Dict]) -> List[Dict]:
        """Process observation data into a consistent format."""
        processed = []
        for obs in observations:
            resource = obs.get("resource", {})
            code = resource.get("code", {}).get("coding", [{}])[0]
            value = resource.get("valueQuantity", {})
            processed.append({
                "code": code.get("code"),
                "system": code.get("system"),
                "display": code.get("display"),
                "value": value.get("value"),
                "unit": value.get("unit"),
                "date": resource.get("effectiveDateTime")
            })
        return processed

    def _process_medications(self, medications: List[Dict]) -> List[Dict]:
        """Process medication data into a consistent format."""
        processed = []
        for med in medications:
            resource = med.get("resource", {})
            medication = resource.get("medicationCodeableConcept", {})
            code = medication.get("coding", [{}])[0]
            processed.append({
                "code": code.get("code"),
                "system": code.get("system"),
                "display": code.get("display"),
                "status": resource.get("status"),
                "intent": resource.get("intent"),
                "date": resource.get("authoredOn")
            })
        return processed

    def _process_conditions(self, conditions: List[Dict]) -> List[Dict]:
        """Process condition data into a consistent format."""
        processed = []
        for cond in conditions:
            resource = cond.get("resource", {})
            code = resource.get("code", {}).get("coding", [{}])[0]
            processed.append({
                "code": code.get("code"),
                "system": code.get("system"),
                "display": code.get("display"),
                "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
                "onset": resource.get("onsetDateTime")
            })
        return processed

    async def _fetch_resource(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """Fetch a single FHIR resource."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.auth_header)
            
            url = f"{self.base_url}/{resource_type}/{resource_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Error fetching {resource_type}: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {resource_type}: {str(e)}")
            return None

    async def _fetch_observations(self, patient_id: str) -> List[Dict]:
        """Fetch all observations for a patient."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.auth_header)
            
            url = f"{self.base_url}/Observation"
            params = {
                'patient': patient_id,
                '_sort': '-date',
                '_count': '100'
            }
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('entry', [])
                return []
        except Exception as e:
            logger.error(f"Error fetching observations: {str(e)}")
            return []

    async def _fetch_medications(self, patient_id: str) -> List[Dict]:
        """Fetch all medications for a patient."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.auth_header)
            
            url = f"{self.base_url}/MedicationRequest"
            params = {
                'patient': patient_id,
                'status': 'active',
                '_sort': '-authoredon',
                '_count': '100'
            }
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('entry', [])
                return []
        except Exception as e:
            logger.error(f"Error fetching medications: {str(e)}")
            return []

    async def _fetch_conditions(self, patient_id: str) -> List[Dict]:
        """Fetch all conditions for a patient."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.auth_header)
            
            url = f"{self.base_url}/Condition"
            params = {
                'patient': patient_id,
                'clinical-status': 'active',
                '_sort': '-onset-date',
                '_count': '100'
            }
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('entry', [])
                return []
        except Exception as e:
            logger.error(f"Error fetching conditions: {str(e)}")
            return []

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()

    async def refresh_patient_data(self, patient_id: str):
        """Force refresh patient data."""
        cache_key = f"patient_{patient_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]
        return await self.get_patient(patient_id)

# Example usage:
# fhir_client = FHIRClient()
# patient = await fhir_client.get_patient("12345")
# print(patient)
