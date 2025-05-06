import httpx
from fastapi import HTTPException
from models import Patient  # Assuming you have a Patient model defined in models.py

class FHIRClient:
    def __init__(self, base_url: str = "http://localhost:5001/fhir/r4"):
        self.base_url = base_url

    async def get_patient(self, patient_id: str) -> Patient:
        """
        Retrieve a patient by ID from the FHIR server.

        Args:
            patient_id (str): The ID of the patient to retrieve.

        Returns:
            Patient: The patient data.

        Raises:
            HTTPException: If the patient is not found or if there is an error in the request.
        """
        url = f"{self.base_url}/Patient/{patient_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 200:
                return Patient(**response.json())  # Assuming Patient model can be instantiated with JSON data
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Patient not found")
            else:
                raise HTTPException(status_code=response.status_code, detail="Error retrieving patient data")

    async def search_patients(self, name: str) -> list[Patient]:
        """
        Search for patients by name.

        Args:
            name (str): The name of the patient to search for.

        Returns:
            list[Patient]: A list of patients matching the search criteria.
        """
        url = f"{self.base_url}/Patient?name={name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 200:
                return [Patient(**patient) for patient in response.json().get("entry", [])]
            else:
                raise HTTPException(status_code=response.status_code, detail="Error searching for patients")

# Example usage:
# fhir_client = FHIRClient()
# patient = await fhir_client.get_patient("12345")
# print(patient)
