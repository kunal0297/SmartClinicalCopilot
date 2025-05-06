import httpx
from fastapi import HTTPException
from models import Patient  # Pydantic model for Patient

class FHIRClient:
    def __init__(self, base_url: str = "http://localhost:5001/fhir/r4"):
        self.base_url = base_url

    async def get_patient(self, patient_id: str) -> Patient:
        """
        Retrieve a patient by ID from the FHIR server.

        Args:
            patient_id (str): The ID of the patient to retrieve.

        Returns:
            Patient: The patient data if found.
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
                raise HTTPException(status_code=response.status_code, detail="Error fetching patient")

# Example usage:
# fhir_client = FHIRClient()
# patient = await fhir_client.get_patient("12345")
# print(patient)
