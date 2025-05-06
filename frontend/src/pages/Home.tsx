import { Box, Typography, Grid, Card, CardContent, CardActions, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to Clinical Decision Support System
      </Typography>
      <Typography variant="body1" paragraph>
        This system helps healthcare providers make informed decisions by analyzing patient data
        and applying clinical rules to identify potential issues and provide recommendations.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2">
                Patient Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View and manage patient records, analyze conditions, and get real-time alerts.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" color="primary" onClick={() => navigate('/patients')}>
                View Patients
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2">
                Clinical Rules
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Browse and manage clinical rules that drive the decision support system.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" color="primary" onClick={() => navigate('/rules')}>
                View Rules
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2">
                System Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monitor system health, performance metrics, and recent activities.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" color="primary" onClick={() => navigate('/status')}>
                Check Status
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 