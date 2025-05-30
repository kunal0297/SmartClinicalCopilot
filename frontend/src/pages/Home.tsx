import { useState, useEffect } from 'react';
import type { Patient } from '../api';
import { Vortex } from '../components/ui/vortex';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Remove unused imports
// import Typography from '@mui/material/Typography';
// import Container from '@mui/material/Container';
// import Grid from '@mui/material/Grid';

const Home = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load demo patients initially using useEffect
  useEffect(() => {
    const fetchDemoPatients = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('http://localhost:8000/demo-patients');
        const data: Patient[] = response.data;
        // Filter out patients with id not starting with "demo-"
        const demoData = data.filter(patient => patient.id.startsWith('demo-'));
        setPatients(demoData);
      } catch (err: any) {
        console.error("Error fetching demo patients:", err);
        setError(err.message || 'Failed to load demo patients');
      } finally {
        setLoading(false);
      }
    };

    fetchDemoPatients();
  }, []); // Empty dependency array means this effect runs once after initial render

  return (
    <div className="min-h-screen w-full overflow-hidden">
       {/* Vortex Background */}
       <Vortex
          backgroundColor="black"
          className="fixed inset-0 z-0 flex items-center justify-center"
          containerClassName="fixed inset-0 z-0"
       />

      {/* Content */}
      <div className="relative z-10 p-6">
        <h1 className="text-4xl font-bold text-white mb-6">Patients</h1>
        
        {error && (
           <div className="text-red-500 mb-4 text-center border border-red-700 p-3 rounded">
             Error: {error}
           </div>
        )}

        {loading ? (
          <div className="text-white text-center">Loading...</div>
        ) : (
          <div className="text-white text-center">
            {patients.length === 0 ? (
              <div>No demo patients found.</div>
            ) : (
              <ul className="list-disc list-inside">
                {patients.map((patient) => (
                  <li key={patient.id}>{patient.demographics?.name || patient.id}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Add links to other sections if needed */}
        <div className="mt-8 text-center">
           <Link to="/alerts" className="text-blue-500 hover:underline mr-4">View Alerts</Link>
           <Link to="/metrics" className="text-blue-500 hover:underline mr-4">View Metrics</Link>
           <Link to="/cohort-analytics" className="text-blue-500 hover:underline">View Cohort Analytics</Link>
        </div>

      </div>
    </div>
  );
};

export default Home;
