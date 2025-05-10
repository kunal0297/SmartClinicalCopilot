import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid as MuiGrid,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { getCohortAnalytics, type CohortAnalytics } from '../api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function CohortAnalytics() {
  const [analytics, setAnalytics] = useState<CohortAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const theme = useTheme();

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await getCohortAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error('Error fetching cohort analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const chartData = React.useMemo(() => {
    if (!analytics) return [];
    return Object.entries(analytics).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value
    }));
  }, [analytics]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>
        Cohort Analytics
      </Typography>

      <MuiGrid container spacing={3}>
        {/* Bar Chart */}
        <MuiGrid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Patient Distribution
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill={theme.palette.primary.main} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </MuiGrid>

        {/* Pie Chart */}
        <MuiGrid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Distribution Overview
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </MuiGrid>

        {/* Summary Cards */}
        <MuiGrid item xs={12}>
          <MuiGrid container spacing={2}>
            {chartData.map((item, index) => (
              <MuiGrid item xs={12} sm={6} md={3} key={item.name}>
                <Paper
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    bgcolor: theme.palette.background.paper,
                    border: `1px solid ${theme.palette.divider}`,
                    '&:hover': {
                      boxShadow: theme.shadows[4],
                      transform: 'translateY(-2px)',
                      transition: 'all 0.3s ease-in-out'
                    }
                  }}
                >
                  <Typography variant="h6" color="primary" gutterBottom>
                    {item.name}
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {item.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Patients
                  </Typography>
                </Paper>
              </MuiGrid>
            ))}
          </MuiGrid>
        </MuiGrid>
      </MuiGrid>
    </Box>
  );
} 