import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

// Create context
const PatientContext = createContext();

// Initial state
const initialState = {
  currentPatient: null,
  patientData: null,
  loading: false,
  error: null,
  clinicalScores: {}
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_CURRENT_PATIENT: 'SET_CURRENT_PATIENT',
  SET_PATIENT_DATA: 'SET_PATIENT_DATA',
  SET_CLINICAL_SCORES: 'SET_CLINICAL_SCORES'
};

// Reducer
function patientReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    case ActionTypes.SET_CURRENT_PATIENT:
      return {
        ...state,
        currentPatient: action.payload
      };
    case ActionTypes.SET_PATIENT_DATA:
      return {
        ...state,
        patientData: action.payload
      };
    case ActionTypes.SET_CLINICAL_SCORES:
      return {
        ...state,
        clinicalScores: {
          ...state.clinicalScores,
          [action.payload.type]: action.payload.score
        }
      };
    default:
      return state;
  }
}

// Provider component
export function PatientProvider({ children }) {
  const [state, dispatch] = useReducer(patientReducer, initialState);

  // Fetch patient data
  const fetchPatientData = async (patientId) => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      
      const response = await axios.get(`/api/patients/${patientId}`);
      
      dispatch({ type: ActionTypes.SET_CURRENT_PATIENT, payload: response.data });
      dispatch({ type: ActionTypes.SET_PATIENT_DATA, payload: response.data });
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
    }
  };

  // Calculate clinical score
  const calculateClinicalScore = async (scoreType) => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      
      const response = await axios.post('/api/clinical-scores/calculate', {
        score_type: scoreType,
        patient_data: state.patientData
      });
      
      dispatch({
        type: ActionTypes.SET_CLINICAL_SCORES,
        payload: {
          type: scoreType,
          score: response.data
        }
      });
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
    }
  };

  // Get SMART on FHIR launch URL
  const getLaunchUrl = async () => {
    try {
      const response = await axios.get('/api/smart/launch');
      return response.data.launch_url;
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
      return null;
    }
  };

  // Effect to fetch patient data when currentPatient changes
  useEffect(() => {
    if (state.currentPatient?.id) {
      fetchPatientData(state.currentPatient.id);
    }
  }, [state.currentPatient?.id]);

  // Context value
  const value = {
    ...state,
    fetchPatientData,
    calculateClinicalScore,
    getLaunchUrl
  };

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
}

// Custom hook
export function usePatient() {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within a PatientProvider');
  }
  return context;
} 