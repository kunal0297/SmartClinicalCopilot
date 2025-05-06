// src/pages/Dashboard.tsx
import React, { useState, useEffect } from "react";
import { Container, Typography, CircularProgress, Box, Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from "@mui/material";
import PatientViewer from "../components/PatientViewer";
import AlertCard from "../components/AlertCard";
import RuleEditor from "../components/RuleEditor";
import { fetchPatient, matchRules, explainRule } from "../api";

const DUMMY_PATIENT_ID = "example_patient_id"; // Replace with real ID or user input

const Dashboard: React.FC = () => {
  const [patient, setPatient] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explanationOpen, setExplanationOpen] = useState(false);
  const [explanationLoading, setExplanationLoading] = useState(false);

  useEffect(() => {
    const loadPatientAndAlerts = async () => {
      try {
        const patientData = await fetchPatient(DUMMY_PATIENT_ID);
        setPatient(patientData);

        const alertData = await matchRules(patientData);
        setAlerts(alertData);
      } catch (error) {
        console.error("Error loading patient or alerts:", error);
      } finally {
        setLoading(false);
      }
    };
    loadPatientAndAlerts();
  }, []);

  const handleRuleSearch = async (ruleText: string) => {
    setLoading(true);
    try {
      // Search rule by querying backend with custom rule text as a patient? (or customize as needed)
      const alertData = await matchRules({ id: "custom", name: [{ text: ruleText }] });
      setAlerts(alertData);
    } catch (error) {
      console.error("Error searching rule:", error);
    }
    setLoading(false);
  };

  const handleExplainRule = async (ruleId: string) => {
    setExplanationLoading(true);
    setExplanationOpen(true);
    try {
      if (!patient) return;
      const result = await explainRule(ruleId, patient);
      setExplanation(result);
    } catch (error) {
      setExplanation("Failed to get explanation.");
      console.error("Explain rule error:", error);
    }
    setExplanationLoading(false);
  };

  const handleCloseExplanation = () => {
    setExplanationOpen(false);
    setExplanation(null);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Clinical Rules Dashboard
      </Typography>
      {loading && <CircularProgress />}
      {!loading && patient && <PatientViewer patient={patient} />}

      <RuleEditor onSubmit={handleRuleSearch} />

      {!loading && alerts.length === 0 && <Typography>No alerts found.</Typography>}

      {alerts.map((alert) => (
        <Box key={alert.rule_id} sx={{ cursor: "pointer" }} onClick={() => handleExplainRule(alert.rule_id)}>
          <AlertCard alert={alert} />
        </Box>
      ))}

      <Dialog open={explanationOpen} onClose={handleCloseExplanation}>
        <DialogTitle>Rule Explanation</DialogTitle>
        <DialogContent>
          {explanationLoading ? (
            <CircularProgress />
          ) : (
            <DialogContentText>{explanation}</DialogContentText>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseExplanation}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Dashboard;
