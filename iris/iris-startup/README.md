# IRIS Startup Folder

This folder contains scripts and resources that are automatically mounted into the InterSystems IRIS for Health CE container at startup. It is designed to facilitate the loading of FHIR resources and any custom startup scripts you may need.

## Folder Structure
iris-startup/ ├── load_fhir_resources.sh # 🚀 Script to load FHIR resources into the IRIS FHIR server ├── SamplePatients/ # Directory for sample FHIR patient/resource JSON files │ └── test_patient.json # Example patient resource └── README.md # Instructions for using this startup folder

Run
Copy code

## Usage Instructions

### 1. Adding FHIR Resources

- Place your FHIR JSON files in the `SamplePatients/` directory. The files should conform to the FHIR standard and be named appropriately (e.g., `test_patient.json`).
- You can add multiple JSON files to this directory, and the `load_fhir_resources.sh` script will upload all of them to the FHIR server when executed.

### 2. Loading FHIR Resources

- The `load_fhir_resources.sh` script is responsible for uploading the FHIR resources to the IRIS FHIR server. This script will be executed manually after the IRIS container is up and running.
- To execute the script, run the following command in your terminal after starting the IRIS container:
  ```bash
  docker exec -it irishealth-ce bash /usr/irissys/Startup/load_fhir_resources.sh
3. Script Details
load_fhir_resources.sh: This script performs the following actions:
Checks if the FHIR server is reachable.
Iterates through all .json files in the SamplePatients/ directory.
Uploads each file to the FHIR server using a POST request.
Reports the success or failure of each upload based on the HTTP response code.
4. Example FHIR Resource
The test_patient.json file is provided as an example. You can modify this file or add new ones based on your requirements. Ensure that the JSON structure adheres to the FHIR specifications.
5. Custom Scripts
You can add additional scripts to this folder if you need to perform other initialization tasks when the IRIS container starts. Just ensure that they are executable and follow the same conventions as load_fhir_resources.sh.
6. Important Notes
Ensure that the IRIS container is fully started before executing the upload script. You can check the container status using:
bash
docker ps
If you encounter issues with the FHIR upload, verify that the FHIR server is accessible at http://localhost:5001/fhir/r4.
7. Version Control
This folder is part of a version-controlled project. When making changes to scripts or resources, ensure you commit your changes with appropriate messages to maintain a clear history of modifications.
Conclusion
This startup folder is a powerful tool for managing FHIR resources in your IRIS for Health CE environment. By following the instructions above, you can easily add, manage, and upload FHIR resources as needed.

For further assistance, refer to the main project README or consult the InterSystems documentation on FHIR and IRIS.

---

This `README.md` provides comprehensive instructions on how to use the `iris-startup` folder, including details on adding FHIR resources, executing scripts, and managing the folder effectively. It also emphasizes the importance of version control, which is crucial for maintaining the integrity of your project. 

Feel free to modify any sections to better fit your project's specif
