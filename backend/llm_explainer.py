import httpx
import json
from fastapi import HTTPException
from models import Patient
from typing import Optional

class FHIRClient:
    def __init__(self, base_url: str = "http://localhost:5001/fhir/r4"):
        self.base_url = base_url

    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Retrieve a patient by ID from the FHIR server.

        Args:
            patient_id (str): The ID of the patient to retrieve.

        Returns:
            Optional[Patient]: The patient data if found, otherwise None.

        Raises:
            HTTPException: For HTTP errors.
        """
        url = f"{self.base_url}/Patient/{patient_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                return Patient(**data)
            elif response.status_code == 404:
                return None
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching patient: {response.text}"
                )

    async def search_patients(self, name: str) -> List[Patient]:
        """
        Search for patients by name.

        Args:
            name (str): The name of the patient to search for.

        Returns:
            List[Patient]: A list of patients matching the search criteria.
        """
        url = f"{self.base_url}/Patient?name={name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                return [Patient(**patient) for patient in data.get("entry", [])]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error searching for patients: {response.text}"
                )

    async def get_patient_history(self, patient_id: str) -> List[Patient]:
        """
        Retrieve the history of a patient's records.

        Args:
            patient_id (str): The ID of the patient.

        Returns:
            List[Patient]: A list of historical patient records.
        """
        url = f"{self.base_url}/Patient/{patient_id}/_history"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                return [Patient(**entry["resource"]) for entry in data.get("entry", [])]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching patient history: {response.text}"
                )

# Example usage:
# fhir_client = FHIRClient()
# patient = await fhir_client.get_patient("12345")
# print(patient)
