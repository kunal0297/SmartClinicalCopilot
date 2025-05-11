import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Chip,
  Divider,
  useTheme,
  Alert,
  CircularProgress,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface ValidationRule {
  id: string;
  name: string;
  description: string;
  type: 'required' | 'format' | 'range' | 'custom';
  status: 'active' | 'inactive';
  severity: 'error' | 'warning' | 'info';
  validation: string;
}

interface ValidationResult {
  ruleId: string;
  status: 'pass' | 'fail';
  message: string;
  timestamp: string;
}

interface ConfigValidationProps {
  open: boolean;
  onClose: () => void;
  onValidate: (config: any) => Promise<ValidationResult[]>;
  onSaveRule: (rule: ValidationRule) => Promise<void>;
  onDeleteRule: (ruleId: string) => Promise<void>;
  rules: ValidationRule[];
  results: ValidationResult[];
}

const ConfigValidation: React.FC<ConfigValidationProps> = ({
  open,
  onClose,
  onValidate,
  onSaveRule,
  onDeleteRule,
  rules,
  results
}) => {
  const theme = useTheme();
  const [selectedRule, setSelectedRule] = useState<ValidationRule | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const handleValidate = async () => {
    setIsValidating(true);
    setError(null);
    try {
      await onValidate({});
    } catch (err) {
      setError('Failed to validate configuration');
    } finally {
      setIsValidating(false);
    }
  };

  const handleSaveRule = async () => {
    if (!selectedRule) return;
    try {
      await onSaveRule(selectedRule);
      setSelectedRule(null);
    } catch (err) {
      setError('Failed to save validation rule');
    }
  };

  const handleDeleteRule = async () => {
    if (!selectedRule) return;
    try {
      await onDeleteRule(selectedRule.id);
      setSelectedRule(null);
      setShowConfirmDelete(false);
    } catch (err) {
      setError('Failed to delete validation rule');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return theme.palette.error.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.text.primary;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircleIcon color="success" />;
      case 'fail':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon color="action" />;
    }
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
          <Typography variant="h6">Configuration Validation</Typography>
          <Box>
            <Tooltip title="Refresh Validation">
              <IconButton onClick={handleValidate} disabled={isValidating}>
                {isValidating ? <CircularProgress size={24} /> : <RefreshIcon />}
              </IconButton>
            </Tooltip>
            <Button onClick={onClose} color="inherit">
              Close
            </Button>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box display="flex" gap={3}>
          {/* Validation Rules */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              Validation Rules
            </Typography>
            <List>
              {rules.map((rule) => (
                <React.Fragment key={rule.id}>
                  <ListItem
                    button
                    selected={selectedRule?.id === rule.id}
                    onClick={() => setSelectedRule(rule)}
                  >
                    <ListItemIcon>
                      {rule.status === 'active' ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <ErrorIcon color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={rule.name}
                      secondary={rule.description}
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={rule.type}
                        size="small"
                        sx={{
                          bgcolor: getSeverityColor(rule.severity),
                          color: 'white',
                        }}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Box>

          {/* Rule Editor */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              Rule Editor
            </Typography>
            {selectedRule ? (
              <Paper sx={{ p: 2 }}>
                <Box display="flex" flexDirection="column" gap={2}>
                  <TextField
                    label="Rule Name"
                    value={selectedRule.name}
                    onChange={(e) =>
                      setSelectedRule({ ...selectedRule, name: e.target.value })
                    }
                    fullWidth
                  />
                  <TextField
                    label="Description"
                    value={selectedRule.description}
                    onChange={(e) =>
                      setSelectedRule({
                        ...selectedRule,
                        description: e.target.value,
                      })
                    }
                    multiline
                    rows={2}
                    fullWidth
                  />
                  <FormControl fullWidth>
                    <InputLabel>Type</InputLabel>
                    <Select
                      value={selectedRule.type}
                      onChange={(e) =>
                        setSelectedRule({
                          ...selectedRule,
                          type: e.target.value as any,
                        })
                      }
                      label="Type"
                    >
                      <MenuItem value="required">Required</MenuItem>
                      <MenuItem value="format">Format</MenuItem>
                      <MenuItem value="range">Range</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel>Severity</InputLabel>
                    <Select
                      value={selectedRule.severity}
                      onChange={(e) =>
                        setSelectedRule({
                          ...selectedRule,
                          severity: e.target.value as any,
                        })
                      }
                      label="Severity"
                    >
                      <MenuItem value="error">Error</MenuItem>
                      <MenuItem value="warning">Warning</MenuItem>
                      <MenuItem value="info">Info</MenuItem>
                    </Select>
                  </FormControl>
                  <TextField
                    label="Validation"
                    value={selectedRule.validation}
                    onChange={(e) =>
                      setSelectedRule({
                        ...selectedRule,
                        validation: e.target.value,
                      })
                    }
                    multiline
                    rows={4}
                    fullWidth
                  />
                  <Box display="flex" gap={1}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveRule}
                    >
                      Save
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => setShowConfirmDelete(true)}
                    >
                      Delete
                    </Button>
                  </Box>
                </Box>
              </Paper>
            ) : (
              <Paper sx={{ p: 2 }}>
                <Typography color="text.secondary" align="center">
                  Select a rule to edit
                </Typography>
              </Paper>
            )}
          </Box>

          {/* Validation Results */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              Validation Results
            </Typography>
            <List>
              {results.map((result, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemIcon>{getStatusIcon(result.status)}</ListItemIcon>
                    <ListItemText
                      primary={result.message}
                      secondary={result.timestamp}
                    />
                  </ListItem>
                  {index < results.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Confirm Delete Dialog */}
      <Dialog
        open={showConfirmDelete}
        onClose={() => setShowConfirmDelete(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            Are you sure you want to delete this validation rule?
          </Alert>
          <Typography>
            This action cannot be undone. All validation results associated with
            this rule will be removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDelete(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteRule}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default ConfigValidation; 