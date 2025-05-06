import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
} from '@mui/material';
import { getPatient, matchRules } from '../api';
import type { Patient, Alert as AlertType } from '../api';

export default function Patients() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    // In a real application, this would fetch a list of patients
    // For now, we'll use a mock patient
    const mockPatient: Patient = {
      id: 'example_patient_id',
      conditions: {
        observations: [
          {
            code: 'blood-pressure',
            display: 'Blood Pressure',
            value: 140,
            unit: 'mmHg',
          },
        ],
        medications: [
          {
            code: 'aspirin',
            display: 'Aspirin',
            status: 'active',
          },
        ],
        conditions: [
          {
            code: 'hypertension',
            display: 'Hypertension',
            status: 'active',
          },
        ],
      },
    };
    setPatients([mockPatient]);
  }, []);

  const handlePatientClick = async (patient: Patient) => {
    setLoading(true);
    setError(null);
    try {
      const patientData = await getPatient(patient.id);
      setSelectedPatient(patientData);
      const patientAlerts = await matchRules(patientData);
      setAlerts(patientAlerts);
      setDialogOpen(true);
    } catch (err) {
      setError('Failed to load patient data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Patients
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Patient ID</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {patients.map((patient) => (
              <TableRow key={patient.id}>
                <TableCell>{patient.id}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    onClick={() => handlePatientClick(patient)}
                    disabled={loading}
                  >
                    View Details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Patient Details</DialogTitle>
        <DialogContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            selectedPatient && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Conditions
                </Typography>
                {selectedPatient.conditions.conditions.map((condition) => (
                  <Typography key={condition.code}>
                    {condition.display} ({condition.status})
                  </Typography>
                ))}

                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Observations
                </Typography>
                {selectedPatient.conditions.observations.map((obs) => (
                  <Typography key={obs.code}>
                    {obs.display}: {obs.value} {obs.unit}
                  </Typography>
                ))}

                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Medications
                </Typography>
                {selectedPatient.conditions.medications.map((med) => (
                  <Typography key={med.code}>
                    {med.display} ({med.status})
                  </Typography>
                ))}

                {alerts.length > 0 && (
                  <>
                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                      Alerts
                    </Typography>
                    {alerts.map((alert) => (
                      <Alert key={alert.rule_id} severity="warning" sx={{ mb: 1 }}>
                        {alert.message}
                        <br />
                        <small>Triggered by: {alert.triggered_by.join(', ')}</small>
                      </Alert>
                    ))}
                  </>
                )}
              </Box>
            )
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 