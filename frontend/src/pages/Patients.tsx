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
  TextField,
  Grid,
} from '@mui/material';
import { getPatient, matchRules } from '../api';
import type { Patient, Alert as AlertType } from '../api';
import axios from 'axios';

export default function Patients() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [patientId, setPatientId] = useState('');

  // Fetch demo patients on mount
  useEffect(() => {
    const fetchDemoPatients = async () => {
      setLoading(true);
      try {
        const res = await axios.get('http://localhost:8000/demo-patients');
        // Map demo patient data to Patient type for table
        const demoPatients = res.data.map((p: any) => ({
          id: p.id,
          demographics: {
            name: p.name && p.name[0] ? `${p.name[0].given?.[0] || ''} ${p.name[0].family || ''}`.trim() : 'N/A',
            gender: p.gender,
            birth_date: p.birthDate,
          },
          conditions: {
            observations: p.observations || [],
            medications: [],
            conditions: p.conditions || [],
          },
        }));
        setPatients(demoPatients);
      } catch (err) {
        setError('Failed to load demo patients');
      } finally {
        setLoading(false);
      }
    };
    fetchDemoPatients();
  }, []);

  const handlePatientSearch = async () => {
    if (!patientId.trim()) {
      setError('Please enter a patient ID');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const patientData = await getPatient(patientId);
      setPatients([patientData]);
    } catch (err) {
      setError('Failed to load patient data. Please check the patient ID.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h4">Patients</Typography>
        </Grid>
        {/* Add more grid items as needed */}
      </Grid>

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
          <Box sx={{ flex: 1 }}>
            <TextField
              fullWidth
              label="Patient ID"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="Enter patient ID from IRIS Health"
              variant="outlined"
            />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Button
              variant="contained"
              onClick={handlePatientSearch}
              disabled={loading}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Search Patient'}
            </Button>
          </Box>
        </Box>
      </Box>

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
              <TableCell>Name</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Gender</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {patients.map((patient) => (
              <TableRow key={patient.id}>
                <TableCell>{patient.id}</TableCell>
                <TableCell>{patient.demographics?.name || 'N/A'}</TableCell>
                <TableCell>{patient.demographics?.age || 'N/A'}</TableCell>
                <TableCell>{patient.demographics?.gender || 'N/A'}</TableCell>
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
                  Demographics
                </Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography><strong>Name:</strong> {selectedPatient.demographics?.name || 'N/A'}</Typography>
                    <Typography><strong>Age:</strong> {selectedPatient.demographics?.age || 'N/A'}</Typography>
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography><strong>Gender:</strong> {selectedPatient.demographics?.gender || 'N/A'}</Typography>
                    <Typography><strong>Birth Date:</strong> {selectedPatient.demographics?.birth_date || 'N/A'}</Typography>
                  </Box>
                </Box>

                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
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