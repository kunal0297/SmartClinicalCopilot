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
  InputLabel,
  Grid,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  FileUpload as FileUploadIcon,
  FileDownload as FileDownloadIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import MonacoEditor from '@monaco-editor/react';

interface ImportExportConfig {
  id: string;
  name: string;
  description: string;
  type: 'json' | 'yaml' | 'toml' | 'env';
  content: string;
  status: 'pending' | 'importing' | 'exporting' | 'completed' | 'error';
  error?: string;
  createdAt: string;
  updatedAt: string;
}

interface ConfigImportExportProps {
  open: boolean;
  onClose: () => void;
  onImport: (file: File) => Promise<void>;
  onExport: (config: ImportExportConfig) => Promise<void>;
  onDelete: (configId: string) => Promise<void>;
  configs: ImportExportConfig[];
}

const ConfigImportExport: React.FC<ConfigImportExportProps> = ({
  open,
  onClose,
  onImport,
  onExport,
  onDelete,
  configs
}) => {
  const theme = useTheme();
  const [selectedConfig, setSelectedConfig] = useState<ImportExportConfig | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importPreview, setImportPreview] = useState<string>('');

  const handleImport = async () => {
    if (!importFile) return;
    setIsProcessing(true);
    setError(null);
    try {
      await onImport(importFile);
      setActiveStep(2);
    } catch (err) {
      setError('Failed to import configuration');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async () => {
    if (!selectedConfig) return;
    setIsProcessing(true);
    setError(null);
    try {
      await onExport(selectedConfig);
    } catch (err) {
      setError('Failed to export configuration');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedConfig) return;
    try {
      await onDelete(selectedConfig.id);
      setSelectedConfig(null);
      setShowConfirmDelete(false);
    } catch (err) {
      setError('Failed to delete configuration');
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImportFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImportPreview(e.target?.result as string);
      };
      reader.readAsText(file);
    }
  };

  const getLanguage = (type: string) => {
    switch (type) {
      case 'json':
        return 'json';
      case 'yaml':
        return 'yaml';
      case 'toml':
        return 'toml';
      case 'env':
        return 'plaintext';
      default:
        return 'plaintext';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <WarningIcon color="warning" />;
      default:
        return <RefreshIcon color="action" />;
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
          <Typography variant="h6">Import/Export Configuration</Typography>
          <Box>
            <Tooltip title="Refresh">
              <IconButton disabled={isProcessing}>
                {isProcessing ? <CircularProgress size={24} /> : <RefreshIcon />}
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

        <Grid container spacing={3}>
          {/* Import/Export Steps */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Stepper activeStep={activeStep} orientation="vertical">
                <Step>
                  <StepLabel>Select Operation</StepLabel>
                  <StepContent>
                    <Box display="flex" gap={2}>
                      <Button
                        variant="contained"
                        startIcon={<FileUploadIcon />}
                        onClick={() => setActiveStep(1)}
                      >
                        Import
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<FileDownloadIcon />}
                        onClick={() => setActiveStep(2)}
                      >
                        Export
                      </Button>
                    </Box>
                  </StepContent>
                </Step>
                <Step>
                  <StepLabel>Import Configuration</StepLabel>
                  <StepContent>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<FileUploadIcon />}
                      >
                        Choose File
                        <input
                          type="file"
                          hidden
                          accept=".json,.yaml,.yml,.toml,.env"
                          onChange={handleFileChange}
                        />
                      </Button>
                      {importFile && (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            File Preview
                          </Typography>
                          <Box height={300}>
                            <MonacoEditor
                              height="100%"
                              language={getLanguage(importFile.name.split('.').pop() || '')}
                              value={importPreview}
                              options={{
                                readOnly: true,
                                minimap: { enabled: false },
                                scrollBeyondLastLine: false,
                                fontSize: 14,
                                wordWrap: 'on',
                              }}
                            />
                          </Box>
                        </Box>
                      )}
                      <Box display="flex" gap={1}>
                        <Button
                          variant="contained"
                          onClick={handleImport}
                          disabled={!importFile || isProcessing}
                        >
                          Import
                        </Button>
                        <Button
                          variant="outlined"
                          onClick={() => setActiveStep(0)}
                        >
                          Back
                        </Button>
                      </Box>
                    </Box>
                  </StepContent>
                </Step>
                <Step>
                  <StepLabel>Export Configuration</StepLabel>
                  <StepContent>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <List>
                        {configs.map((config) => (
                          <React.Fragment key={config.id}>
                            <ListItem
                              button
                              selected={selectedConfig?.id === config.id}
                              onClick={() => setSelectedConfig(config)}
                            >
                              <ListItemIcon>
                                {getStatusIcon(config.status)}
                              </ListItemIcon>
                              <ListItemText
                                primary={config.name}
                                secondary={config.description}
                              />
                              <ListItemSecondaryAction>
                                <Chip
                                  label={config.type}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                            <Divider />
                          </React.Fragment>
                        ))}
                      </List>
                      <Box display="flex" gap={1}>
                        <Button
                          variant="contained"
                          onClick={handleExport}
                          disabled={!selectedConfig || isProcessing}
                        >
                          Export
                        </Button>
                        <Button
                          variant="outlined"
                          onClick={() => setActiveStep(0)}
                        >
                          Back
                        </Button>
                      </Box>
                    </Box>
                  </StepContent>
                </Step>
              </Stepper>
            </Paper>
          </Grid>

          {/* Configuration List */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Configurations
              </Typography>
              <List>
                {configs.map((config) => (
                  <React.Fragment key={config.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(config.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={config.name}
                        secondary={
                          <>
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.primary"
                            >
                              {config.description}
                            </Typography>
                            {config.error && (
                              <Typography
                                component="span"
                                variant="body2"
                                color="error"
                                display="block"
                              >
                                {config.error}
                              </Typography>
                            )}
                          </>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box display="flex" gap={1}>
                          <Chip
                            label={config.type}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <IconButton
                            edge="end"
                            onClick={() => {
                              setSelectedConfig(config);
                              setShowConfirmDelete(true);
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
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
            Are you sure you want to delete this configuration?
          </Alert>
          <Typography>
            This action cannot be undone. The configuration will be permanently
            removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDelete(false)}>Cancel</Button>
          <Button
            onClick={handleDelete}
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

export default ConfigImportExport; 