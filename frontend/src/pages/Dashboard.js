import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useAlerts } from '../context/AlertContext';
import { usePatient } from '../context/PatientContext';
import AlertMetricsChart from '../components/AlertMetricsChart';
import ClinicalScoresCard from '../components/ClinicalScoresCard';
import RecentAlertsList from '../components/RecentAlertsList';

function Dashboard() {
  const history = useHistory();
  const { alerts, metrics, fetchAlerts, fetchMetrics } = useAlerts();
  const { currentPatient, clinicalScores, calculateClinicalScore } = usePatient();

  useEffect(() => {
    // Fetch initial data
    fetchAlerts();
    fetchMetrics();
  }, [fetchAlerts, fetchMetrics]);

  const handlePatientSelect = async (patientId) => {
    history.push(`/patient/${patientId}`);
  };

  const handleCalculateScore = async (scoreType) => {
    if (currentPatient) {
      await calculateClinicalScore(scoreType);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Clinical Decision Support Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<AssessmentIcon />}
                  onClick={() => handleCalculateScore('CHA2DS2-VASc')}
                >
                  Calculate CHA₂DS₂-VASc
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<AssessmentIcon />}
                  onClick={() => handleCalculateScore('Wells')}
                >
                  Calculate Wells Score
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<TimelineIcon />}
                  onClick={() => history.push('/metrics')}
                >
                  View Metrics
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={() => history.push('/settings')}
                >
                  Settings
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Alert Metrics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Alert Metrics
            </Typography>
            <AlertMetricsChart metrics={metrics} />
          </Paper>
        </Grid>

        {/* Clinical Scores */}
        <Grid item xs={12} md={4}>
          <ClinicalScoresCard
            scores={clinicalScores}
            onCalculate={handleCalculateScore}
          />
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <RecentAlertsList alerts={alerts.slice(0, 5)} />
          </Paper>
        </Grid>

        {/* Top Rules */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Alerting Rules
              </Typography>
              <Box sx={{ mt: 2 }}>
                {metrics.topRules.map((rule) => (
                  <Box key={rule.rule_id} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">
                      Rule {rule.rule_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Alerts: {rule.alert_count} | Overrides: {rule.override_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Override Rate: {(rule.override_rate * 100).toFixed(1)}%
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                  </Box>
                ))}
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                startIcon={<WarningIcon />}
                onClick={() => history.push('/alerts')}
              >
                View All Rules
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body1">
                  Total Alerts: {metrics.totalAlerts}
                </Typography>
                <Typography variant="body1">
                  Total Overrides: {metrics.totalOverrides}
                </Typography>
                <Typography variant="body1">
                  Overall Override Rate: {(metrics.overrideRate * 100).toFixed(1)}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard; 