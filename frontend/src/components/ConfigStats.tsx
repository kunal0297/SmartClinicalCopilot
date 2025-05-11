import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Paper,
  useTheme,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  History as HistoryIcon
} from '@mui/icons-material';

interface ConfigStatsProps {
  open: boolean;
  onClose: () => void;
  stats: {
    totalConfigs: number;
    activeConfigs: number;
    encryptedConfigs: number;
    lastUpdated: string;
    accessCount: number;
    errorCount: number;
    avgResponseTime: number;
    cacheHitRate: number;
    memoryUsage: number;
    diskUsage: number;
    operationHistory: Array<{
      type: string;
      count: number;
      timestamp: string;
    }>;
    errorDistribution: Array<{
      type: string;
      count: number;
    }>;
    accessPatterns: Array<{
      time: string;
      count: number;
    }>;
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ConfigStats: React.FC<ConfigStatsProps> = ({ open, onClose, stats }) => {
  const theme = useTheme();

  const StatCard = ({ title, value, icon, color }: any) => (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
      }}
    >
      <Box display="flex" alignItems="center" mb={1}>
        {icon}
        <Typography variant="h6" component="div" sx={{ ml: 1 }}>
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" component="div" color={color}>
        {value}
      </Typography>
    </Paper>
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: theme.shadows[4],
        },
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Configuration Statistics</Typography>
          <Box>
            <Tooltip title="Refresh Stats">
              <IconButton>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button onClick={onClose} color="inherit">
              Close
            </Button>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ flexGrow: 1 }}>
          <Grid container spacing={3}>
            {/* Key Metrics */}
            <Grid item xs={12} md={3}>
              <StatCard
                title="Total Configs"
                value={stats.totalConfigs}
                icon={<StorageIcon color="primary" />}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <StatCard
                title="Active Configs"
                value={stats.activeConfigs}
                icon={<SpeedIcon color="success" />}
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <StatCard
                title="Encrypted Configs"
                value={stats.encryptedConfigs}
                icon={<SecurityIcon color="warning" />}
                color="warning"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <StatCard
                title="Access Count"
                value={stats.accessCount}
                icon={<HistoryIcon color="info" />}
                color="info"
              />
            </Grid>

            {/* Performance Metrics */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Response Time Trend
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stats.accessPatterns}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="count"
                        stroke={theme.palette.primary.main}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Error Distribution
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={stats.errorDistribution}
                        dataKey="count"
                        nameKey="type"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {stats.errorDistribution.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>

            {/* System Metrics */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  System Metrics
                </Typography>
                <Box sx={{ flexGrow: 1 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">Memory Usage</Typography>
                          <Typography variant="body2">
                            {stats.memoryUsage}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={stats.memoryUsage}
                          color={stats.memoryUsage > 80 ? 'error' : 'primary'}
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">Disk Usage</Typography>
                          <Typography variant="body2">{stats.diskUsage}%</Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={stats.diskUsage}
                          color={stats.diskUsage > 80 ? 'error' : 'primary'}
                        />
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </Paper>
            </Grid>

            {/* Operation History */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Operations
                </Typography>
                <List>
                  {stats.operationHistory.map((operation, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <InfoIcon color="action" />
                        </ListItemIcon>
                        <ListItemText
                          primary={operation.type}
                          secondary={operation.timestamp}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {operation.count} operations
                        </Typography>
                      </ListItem>
                      {index < stats.operationHistory.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfigStats; 