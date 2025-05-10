import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Components
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import PatientView from './pages/PatientView';
import AlertsView from './pages/AlertsView';
import MetricsView from './pages/MetricsView';
import Settings from './pages/Settings';

// Context
import { AlertProvider } from './context/AlertContext';
import { PatientProvider } from './context/PatientContext';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize app
    const initializeApp = async () => {
      try {
        // Check if we're in a SMART on FHIR context
        const isSmartContext = window.location.href.includes('launch');
        
        if (isSmartContext) {
          // Initialize SMART on FHIR
          await window.FHIR.oauth2.ready();
        }
        
        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    initializeApp();
  }, []);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        Loading...
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        color="error.main"
      >
        Error: {error}
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AlertProvider>
        <PatientProvider>
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              <Navbar />
              <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
                <Switch>
                  <Route exact path="/" component={Dashboard} />
                  <Route path="/patient/:id" component={PatientView} />
                  <Route path="/alerts" component={AlertsView} />
                  <Route path="/metrics" component={MetricsView} />
                  <Route path="/settings" component={Settings} />
                </Switch>
              </Box>
            </Box>
          </Router>
        </PatientProvider>
      </AlertProvider>
    </ThemeProvider>
  );
}

export default App; 