import axios from 'axios';

// Resolve the API base URL from the Vite environment so the same build works
// in local development (http://localhost:8000) and in Docker/production.
const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Patient {
  id: string;
  // FHIR-style name and demographics as returned by the backend
  name?: Array<{ given?: string[] | string; family?: string }>;
  gender?: string;
  birthDate?: string;
  demographics?: {
    name?: string;
    age?: number;
    gender?: string;
    birth_date?: string;
  };
  conditions: {
    observations: Array<{
      code: string;
      display: string;
      value: number;
      unit: string;
    }>;
    medications: Array<{
      code: string;
      display: string;
      status: string;
    }>;
    conditions: Array<{
      code: string;
      display: string;
      status: string;
    }>;
  };
}

export interface Alert {
  rule_id: string;
  message: string;
  severity: string;
  triggered_by: string[];
}

export interface Rule {
  id: string;
  name: string;
  description: string;
  conditions: Array<{
    type: string;
    code: string;
    operator: string;
    value: any;
  }>;
  actions: Array<{
    type: string;
    message: string;
  }>;
  severity: string;
}

export interface CohortAnalytics {
  diabetics: number;
  hypertensives: number;
  [key: string]: number;
}

export const getPatient = async (patientId: string): Promise<Patient> => {
  const response = await api.get(`/patients/${patientId}`);
  return response.data;
};

export const matchRules = async (patient: Patient): Promise<Alert[]> => {
  const response = await api.post('/match-rules', patient);
  return response.data;
};

export const suggestRules = async (prefix: string): Promise<string[]> => {
  const response = await api.get('/suggest-rules', { params: { prefix } });
  return response.data.suggestions;
};

export const explainRule = async (ruleId: string, patient: Patient): Promise<string> => {
  // The backend expects rule_id as a query parameter and the patient as the body.
  const response = await api.post('/explain-rule', patient, {
    params: { rule_id: ruleId },
  });
  return response.data.explanation;
};

export const getCohortAnalytics = async (): Promise<CohortAnalytics> => {
  const response = await api.get('/cohort-analytics');
  return response.data;
}; 