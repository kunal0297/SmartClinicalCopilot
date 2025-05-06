import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Patient {
  id: string;
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
  const response = await api.post('/explain-rule', { rule_id: ruleId, patient });
  return response.data.explanation;
}; 