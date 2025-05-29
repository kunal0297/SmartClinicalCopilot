import { createContext, useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';

interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: string;
  mrn: string; // Medical Record Number
}

interface PatientData {
  demographics: {
    age: number;
    gender: string;
    ethnicity: string;
    race: string;
    language: string;
  };
  medicalHistory: {
    conditions: Array<{
      code: string;
      display: string;
      system: string;
    }>;
    medications: Array<{
      code: string;
      display: string;
      dosage: string;
      frequency: string;
    }>;
    allergies: Array<{
      substance: string;
      severity: string;
      reaction: string;
    }>;
  };
  vitalSigns: {
    bloodPressure: string;
    heartRate: number;
    temperature: number;
    respiratoryRate: number;
    oxygenSaturation: number;
  };
}

interface ClinicalScore {
  value: number;
  date: string;
  type: string;
  interpretation?: string;
}

interface PatientState {
  currentPatient: Patient | null;
  patientData: PatientData | null;
  loading: boolean;
  error: string | null;
  clinicalScores: Record<string, ClinicalScore>;
}

interface PatientContextType extends PatientState {
  fetchPatientData: () => Promise<void>;
  setCurrentPatient: (patient: Patient | null) => void;
  setPatientData: (data: PatientData | null) => void;
  setClinicalScores: (scores: Record<string, ClinicalScore>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const PatientContext = createContext<PatientContextType | null>(null);

export const PatientProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPatient, setCurrentPatient] = useState<Patient | null>(null);
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [clinicalScores, setClinicalScores] = useState<Record<string, ClinicalScore>>({});

  const fetchPatientData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!currentPatient?.id) {
        throw new Error('No patient selected');
      }

      const response = await axios.get<{
        data: PatientData;
        status: string;
        message?: string;
      }>(`/api/patients/${currentPatient.id}`);

      if (response.data.status === 'error') {
        throw new Error(response.data.message || 'Failed to fetch patient data');
      }

      setPatientData(response.data.data);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.message || err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
      setPatientData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentPatient) {
      fetchPatientData();
    } else {
      setPatientData(null);
      setClinicalScores({});
    }
  }, [currentPatient]);

  const contextValue: PatientContextType = {
    currentPatient,
    patientData,
    loading,
    error,
    clinicalScores,
    fetchPatientData,
    setCurrentPatient,
    setPatientData,
    setClinicalScores,
    setLoading,
    setError
  };

  return (
    <PatientContext.Provider value={contextValue}>
      {children}
    </PatientContext.Provider>
  );
};

export default PatientContext;