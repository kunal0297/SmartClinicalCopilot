import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useAlerts } from '../context/AlertContext';

function RecentAlertsList({ alerts }) {
  const { overrideAlert } = useAlerts();

  const getSeverityColor = (confidence) => {
    if (confidence >= 0.8) return 'error';
    if (confidence >= 0.5) return 'warning';
    return 'info';
  };

  const handleOverride = async (alertId) => {
    const reason = window.prompt('Please enter override reason:');
    if (reason) {
      await overrideAlert(alertId, reason);
    }
  };

  return (
    <List>
      {alerts.map((alert) => (
        <ListItem
          key={alert.id}
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            mb: 1,
            '&:hover': {
              backgroundColor: 'action.hover'
            }
          }}
        >
          <ListItemIcon>
            <WarningIcon color={getSeverityColor(alert.confidence)} />
          </ListItemIcon>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1">
                  Rule {alert.rule_id}
                </Typography>
                <Chip
                  size="small"
                  label={`${(alert.confidence * 100).toFixed(0)}% confidence`}
                  color={getSeverityColor(alert.confidence)}
                />
              </Box>
            }
            secondary={
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {alert.explanation}
                </Typography>
                {alert.details && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Details:
                    </Typography>
                    {Object.entries(alert.details).map(([key, value]) => (
                      <Typography key={key} variant="body2" color="text.secondary">
                        {key}: {value}
                      </Typography>
                    ))}
                  </Box>
                )}
              </Box>
            }
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="View Details">
              <IconButton size="small">
                <InfoIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Override Alert">
              <IconButton
                size="small"
                onClick={() => handleOverride(alert.id)}
              >
                <CheckCircleIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </ListItem>
      ))}
      {alerts.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
          No recent alerts
        </Typography>
      )}
    </List>
  );
}

export default RecentAlertsList; 