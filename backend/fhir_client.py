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
from fhirclient.models.patient import Patient
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.observation import Observation
from fhirclient.models.condition import Condition
from requests.auth import HTTPBasicAuth
import requests
from functools import lru_cache
import redis

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FHIR_BASE_URL = os.getenv('FHIR_BASE_URL', 'http://localhost:52773/csp/healthshare/fhir/r4')
IRIS_USERNAME = os.getenv('IRIS_USERNAME', 'SuperUser')
IRIS_PASSWORD = os.getenv('IRIS_PASSWORD', 'SYS')

def safe_get(d, keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, {})
        else:
            return default
    return d or default

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return None

class FHIRClient:
    def __init__(self):
        self.settings = {
            'app_id': os.getenv('FHIR_APP_ID', 'smart-clinical-copilot'),
            'api_base': FHIR_BASE_URL,
            'redirect_uri': os.getenv('FHIR_REDIRECT_URI', 'http://localhost:3000/callback'),
            'launch_url': os.getenv('FHIR_LAUNCH_URL', 'http://localhost:3000/launch')
        }
        self.smart = None
        # Try to use Redis for distributed cache, fallback to in-memory TTLCache
        try:
            self.redis = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=0)
            self.redis.ping()
            self.use_redis = True
        except Exception:
            self.redis = None
            self.use_redis = False
        self.cache = TTLCache(maxsize=500, ttl=900)  # fallback in-memory cache
        self.session = None
        self.auth = HTTPBasicAuth(IRIS_USERNAME, IRIS_PASSWORD)

    async def initialize(self, launch_token: Optional[str] = None):
        """Initialize FHIR client with SMART on FHIR context"""
        try:
            if launch_token:
                self.smart = client.FHIRClient(settings=self.settings)
                self.smart.authorize(launch_token)
            else:
                # For development/testing without real EHR
                self.smart = client.FHIRClient(settings=self.settings)
                self.smart.authorize()
        except Exception as e:
            logger.error(f"Error initializing FHIR client: {str(e)}")
            raise

    def get_launch_url(self) -> str:
        """Get SMART on FHIR launch URL"""
        return f"{self.settings['launch_url']}?iss={self.settings['api_base']}"

    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive patient data from FHIR server, robust to missing fields and fast. Uses Redis cache if available."""
        cache_key = f"patient_{patient_id}"
        # Try Redis cache first
        if self.use_redis:
            cached = self.redis.get(cache_key)
            if cached:
                import json
                return json.loads(cached)
        elif cache_key in self.cache:
            return self.cache[cache_key]
        try:
            if not self.smart:
                await self.initialize()
            # Batch fetch all resources in parallel for speed
            patient_task = asyncio.to_thread(Patient.read, patient_id, self.smart.server)
            meds_task = asyncio.to_thread(self._get_medications, patient_id)
            labs_task = asyncio.to_thread(self._get_lab_results, patient_id)
            conds_task = asyncio.to_thread(self._get_conditions, patient_id)
            patient, medications, labs, conditions = await asyncio.gather(
                patient_task, meds_task, labs_task, conds_task
            )
            # Defensive mapping (same as before)
            name_obj = patient.name[0] if patient.name else None
            given = name_obj.given[0] if name_obj and name_obj.given else ""
            family = name_obj.family if name_obj and name_obj.family else ""
            gender = patient.gender or "unknown"
            birth_date = parse_date(patient.birthDate.isostring) if getattr(patient, 'birthDate', None) and getattr(patient.birthDate, 'isostring', None) else None
            med_list = []
            for med in medications:
                med_list.append({
                    "code": med.get("name", ""),
                    "system": "",
                    "display": med.get("name", ""),
                    "status": med.get("status", ""),
                    "intent": "",
                    "date": parse_date(med.get("start_date", None))
                })
            obs_list = []
            for lab in labs:
                obs_list.append({
                    "code": lab.get("code", ""),
                    "system": "",
                    "display": lab.get("name", ""),
                    "value": lab.get("value", 0),
                    "unit": lab.get("unit", ""),
                    "date": parse_date(lab.get("date", None))
                })
            cond_list = []
            for cond in conditions:
                cond_list.append({
                    "code": cond.get("code", ""),
                    "system": "",
                    "display": cond.get("name", ""),
                    "status": cond.get("severity", ""),
                    "onset": parse_date(cond.get("onset_date", None))
                })
            patient_data = {
                "id": patient_id,
                "name": [{"given": given, "family": family}],
                "gender": gender,
                "birthDate": birth_date,
                "conditions": {
                    "medications": med_list,
                    "observations": obs_list,
                    "conditions": cond_list
                }
            }
            # Store in Redis or fallback cache
            if self.use_redis:
                import json
                self.redis.setex(cache_key, 900, json.dumps(patient_data))
            else:
                self.cache[cache_key] = patient_data
            return patient_data
        except Exception as e:
            logger.error(f"Error getting patient data: {str(e)}")
            raise

    def _get_medications(self, patient_id: str) -> list:
        """Get active medications for a patient"""
        try:
            search = MedicationRequest.where(struct={'patient': patient_id, 'status': 'active'})
            medications = search.perform_resources(self.smart.server)
            
            return [{
                "id": med.id,
                "name": med.medicationCodeableConcept.text,
                "type": self._get_medication_type(med),
                "start_date": med.authoredOn.isostring if med.authoredOn else None,
                "status": med.status
            } for med in medications]
            
        except Exception as e:
            logger.error(f"Error getting medications: {str(e)}")
            return []

    def _get_lab_results(self, patient_id: str) -> list:
        """Get recent lab results for a patient"""
        try:
            search = Observation.where(struct={'patient': patient_id})
            labs = search.perform_resources(self.smart.server)
            
            return [{
                "id": lab.id,
                "code": lab.code.coding[0].code if lab.code and lab.code.coding else None,
                "name": lab.code.text if lab.code else None,
                "value": lab.valueQuantity.value if lab.valueQuantity else None,
                "unit": lab.valueQuantity.unit if lab.valueQuantity else None,
                "date": lab.effectiveDateTime.isostring if lab.effectiveDateTime else None
            } for lab in labs]
            
        except Exception as e:
            logger.error(f"Error getting lab results: {str(e)}")
            return []

    def _get_conditions(self, patient_id: str) -> list:
        """Get active conditions for a patient"""
        try:
            search = Condition.where(struct={'patient': patient_id, 'clinical-status': 'active'})
            conditions = search.perform_resources(self.smart.server)
            
            return [{
                "id": cond.id,
                "code": cond.code.coding[0].code if cond.code and cond.code.coding else None,
                "name": cond.code.text if cond.code else None,
                "onset_date": cond.onsetDateTime.isostring if cond.onsetDateTime else None,
                "severity": cond.severity.text if cond.severity else None
            } for cond in conditions]
            
        except Exception as e:
            logger.error(f"Error getting conditions: {str(e)}")
            return []

    def _extract_demographics(self, patient: Patient) -> Dict[str, Any]:
        """Extract relevant demographics from FHIR Patient resource"""
        return {
            "id": patient.id,
            "name": f"{patient.name[0].given[0]} {patient.name[0].family}" if patient.name else None,
            "gender": patient.gender,
            "birth_date": patient.birthDate.isostring if patient.birthDate else None,
            "age": self._calculate_age(patient.birthDate.isostring) if patient.birthDate else None
        }

    def _get_medication_type(self, medication: MedicationRequest) -> str:
        """Determine medication type from FHIR resource"""
        # This would be more sophisticated in production
        if medication.medicationCodeableConcept and medication.medicationCodeableConcept.coding:
            code = medication.medicationCodeableConcept.coding[0].code
            # Map medication codes to types
            if code.startswith('NSAID'):
                return "NSAID"
            elif code.startswith('ACE'):
                return "ACE Inhibitor"
            # Add more mappings
        return "Unknown"

    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date"""
        from datetime import datetime
        birth = datetime.fromisoformat(birth_date)
        today = datetime.now()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

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
            
            url = f"{self.settings['api_base']}/{resource_type}/{resource_id}"
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
            
            url = f"{self.settings['api_base']}/Observation"
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
            
            url = f"{self.settings['api_base']}/MedicationRequest"
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
            
            url = f"{self.settings['api_base']}/Condition"
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

    def search_resources(self, resource_type: str, params: dict = None) -> List[dict]:
        """Search FHIR resources of a given type using IRIS Health FHIR endpoint."""
        url = f"{FHIR_BASE_URL}/{resource_type}"
        try:
            response = requests.get(url, params=params, auth=self.auth, headers={"Accept": "application/fhir+json"})
            response.raise_for_status()
            bundle = response.json()
            return [entry['resource'] for entry in bundle.get('entry', [])]
        except Exception as e:
            logger.error(f"Error searching {resource_type}: {str(e)}")
            return []

# Example usage:
# fhir_client = FHIRClient()
# patient = await fhir_client.get_patient("12345")
# print(patient)
