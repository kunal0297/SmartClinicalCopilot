// src/api.ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000", // Backend URL
  headers: {
    "Content-Type": "application/json",
  },
});

// Fetch Patient by ID
export const fetchPatient = async (patientId: string) => {
  const response = await api.get(\`/patients/\${patientId}\`);
  return response.data;
};

// Match clinical rules for patient
export const matchRules = async (patientData: any) => {
  const response = await api.post("/match-rules", { patient: patientData });
  return response.data; // Array of alerts
};

// Request explanation for a clinical rule
export const explainRule = async (ruleId: string, patientData: any) => {
  const response = await api.post("/explain-rule", {
    rule_id: ruleId,
    patient: patientData,
  });
  return response.data.explanation;
};

export default api;
