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
  Divider,
  Tooltip,
  IconButton,
  Card,
  CardContent
} from '@mui/material';
import {
  Refresh as RefreshIcon
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
      timestamp: string;
      operation: string;
      status: string;
    }>;
    errorDistribution: Array<{
      type: string;
      count: number;
    }>;
    accessPatterns: Array<{
      pattern: string;
      count: number;
    }>;
  };
}

const ConfigStats: React.FC<ConfigStatsProps> = ({ open, onClose, stats }) => {
  const theme = useTheme();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatBytes = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

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
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Configuration Overview
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Total Configurations"
                      secondary={stats.totalConfigs}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Active Configurations"
                      secondary={stats.activeConfigs}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Encrypted Configurations"
                      secondary={stats.encryptedConfigs}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Last Updated"
                      secondary={formatDate(stats.lastUpdated)}
                    />
                  </ListItem>
                </List>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Performance Metrics
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Access Count"
                        secondary={stats.accessCount}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Error Count"
                        secondary={stats.errorCount}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Average Response Time"
                        secondary={`${stats.avgResponseTime.toFixed(2)}ms`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Cache Hit Rate"
                        secondary={`${(stats.cacheHitRate * 100).toFixed(1)}%`}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Resource Usage
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Memory Usage
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(stats.memoryUsage / 1024) * 100}
                    />
                    <Typography variant="caption">
                      {formatBytes(stats.memoryUsage)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" gutterBottom>
                      Disk Usage
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(stats.diskUsage / 1024) * 100}
                    />
                    <Typography variant="caption">
                      {formatBytes(stats.diskUsage)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Operations
                  </Typography>
                  <List>
                    {stats.operationHistory.map((operation, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText
                            primary={operation.operation}
                            secondary={formatDate(operation.timestamp)}
                          />
                          <Typography
                            variant="caption"
                            color={operation.status === 'success' ? 'success.main' : 'error.main'}
                          >
                            {operation.status}
                          </Typography>
                        </ListItem>
                        {index < stats.operationHistory.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
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