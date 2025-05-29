import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
// Remove React import since it's not directly used
import { useMemo, useState } from 'react';
import Home from './pages/Home';
import Patients from './pages/Patients';
import Rules from './pages/Rules';
import CohortAnalytics from './pages/CohortAnalytics';
import Navbar from './components/Navbar';
import { PatientProvider } from './context/PatientContext.jsx';
import VortexBackground from './components/VortexBackground';

function App() {
  const [mode, setMode] = useState<'light' | 'dark'>('dark');
  const toggleMode = () => setMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      primary: { main: '#1976d2' },
      secondary: { main: '#dc004e' },
    },
  }), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {mode === 'dark' && <VortexBackground />}
      <PatientProvider>
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
            <Navbar mode={mode} toggleMode={toggleMode} />
            <Container component="main" maxWidth={false} sx={{ mt: 4, mb: 4, flex: 1, width: '100%' }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/rules" element={<Rules />} />
                <Route path="/patients" element={<Patients />} />
                <Route path="/cohort-analytics" element={<CohortAnalytics />} />
              </Routes>
            </Container>
            <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)', width: '100vw' }}>
              <span style={{ color: 'white', textAlign: 'center', display: 'block' }}>
                {'© '}
                {new Date().getFullYear()} {' Smart Clinical Copilot'}
              </span>
            </Box>
          </Box>
        </Router>
      </PatientProvider>
    </ThemeProvider>
  );
}

export default App;
