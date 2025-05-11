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
  Grid
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as ContentCopyIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import MonacoEditor from '@monaco-editor/react';

interface Template {
  id: string;
  name: string;
  description: string;
  type: 'json' | 'yaml' | 'toml' | 'env';
  content: string;
  variables: string[];
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

interface ConfigTemplateProps {
  open: boolean;
  onClose: () => void;
  onSaveTemplate: (template: Template) => Promise<void>;
  onDeleteTemplate: (templateId: string) => Promise<void>;
  onApplyTemplate: (templateId: string, variables: Record<string, string>) => Promise<any>;
  templates: Template[];
}

const ConfigTemplate: React.FC<ConfigTemplateProps> = ({
  open,
  onClose,
  onSaveTemplate,
  onDeleteTemplate,
  onApplyTemplate,
  templates
}) => {
  const theme = useTheme();
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [variables, setVariables] = useState<Record<string, string>>({});
  const [previewContent, setPreviewContent] = useState<string>('');

  const handleSaveTemplate = async () => {
    if (!selectedTemplate) return;
    setIsProcessing(true);
    setError(null);
    try {
      await onSaveTemplate(selectedTemplate);
      setSelectedTemplate(null);
    } catch (err) {
      setError('Failed to save template');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteTemplate = async () => {
    if (!selectedTemplate) return;
    try {
      await onDeleteTemplate(selectedTemplate.id);
      setSelectedTemplate(null);
      setShowConfirmDelete(false);
    } catch (err) {
      setError('Failed to delete template');
    }
  };

  const handleApplyTemplate = async () => {
    if (!selectedTemplate) return;
    setIsProcessing(true);
    setError(null);
    try {
      const result = await onApplyTemplate(selectedTemplate.id, variables);
      setPreviewContent(JSON.stringify(result, null, 2));
    } catch (err) {
      setError('Failed to apply template');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVariableChange = (name: string, value: string) => {
    setVariables((prev) => ({
      ...prev,
      [name]: value,
    }));
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
          <Typography variant="h6">Configuration Templates</Typography>
          <Box>
            <Tooltip title="Refresh Templates">
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
          {/* Template List */}
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Templates
            </Typography>
            <List>
              {templates.map((template) => (
                <React.Fragment key={template.id}>
                  <ListItem
                    button
                    selected={selectedTemplate?.id === template.id}
                    onClick={() => setSelectedTemplate(template)}
                  >
                    <ListItemIcon>
                      <DescriptionIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={template.name}
                      secondary={template.description}
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={template.type}
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
          </Grid>

          {/* Template Editor */}
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Template Editor
            </Typography>
            {selectedTemplate ? (
              <Box display="flex" flexDirection="column" gap={2}>
                <Paper sx={{ p: 2 }}>
                  <Box display="flex" flexDirection="column" gap={2}>
                    <TextField
                      label="Template Name"
                      value={selectedTemplate.name}
                      onChange={(e) =>
                        setSelectedTemplate({
                          ...selectedTemplate,
                          name: e.target.value,
                        })
                      }
                      fullWidth
                    />
                    <TextField
                      label="Description"
                      value={selectedTemplate.description}
                      onChange={(e) =>
                        setSelectedTemplate({
                          ...selectedTemplate,
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
                        value={selectedTemplate.type}
                        onChange={(e) =>
                          setSelectedTemplate({
                            ...selectedTemplate,
                            type: e.target.value as any,
                          })
                        }
                        label="Type"
                      >
                        <MenuItem value="json">JSON</MenuItem>
                        <MenuItem value="yaml">YAML</MenuItem>
                        <MenuItem value="toml">TOML</MenuItem>
                        <MenuItem value="env">ENV</MenuItem>
                      </Select>
                    </FormControl>
                    <Box height={300}>
                      <MonacoEditor
                        height="100%"
                        language={getLanguage(selectedTemplate.type)}
                        value={selectedTemplate.content}
                        onChange={(value) =>
                          setSelectedTemplate({
                            ...selectedTemplate,
                            content: value || '',
                          })
                        }
                        options={{
                          minimap: { enabled: false },
                          scrollBeyondLastLine: false,
                          fontSize: 14,
                          wordWrap: 'on',
                        }}
                      />
                    </Box>
                    <Box display="flex" gap={1}>
                      <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSaveTemplate}
                        disabled={isProcessing}
                      >
                        Save
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => setShowConfirmDelete(true)}
                        disabled={isProcessing}
                      >
                        Delete
                      </Button>
                    </Box>
                  </Box>
                </Paper>

                {/* Variables */}
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Variables
                  </Typography>
                  <Grid container spacing={2}>
                    {selectedTemplate.variables.map((variable) => (
                      <Grid item xs={12} md={6} key={variable}>
                        <TextField
                          label={variable}
                          value={variables[variable] || ''}
                          onChange={(e) =>
                            handleVariableChange(variable, e.target.value)
                          }
                          fullWidth
                        />
                      </Grid>
                    ))}
                  </Grid>
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      startIcon={<ContentCopyIcon />}
                      onClick={handleApplyTemplate}
                      disabled={isProcessing}
                    >
                      Apply Template
                    </Button>
                  </Box>
                </Paper>

                {/* Preview */}
                {previewContent && (
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Preview
                    </Typography>
                    <Box height={300}>
                      <MonacoEditor
                        height="100%"
                        language="json"
                        value={previewContent}
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          scrollBeyondLastLine: false,
                          fontSize: 14,
                          wordWrap: 'on',
                        }}
                      />
                    </Box>
                  </Paper>
                )}
              </Box>
            ) : (
              <Paper sx={{ p: 2 }}>
                <Typography color="text.secondary" align="center">
                  Select a template to edit
                </Typography>
              </Paper>
            )}
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
            Are you sure you want to delete this template?
          </Alert>
          <Typography>
            This action cannot be undone. All configurations using this template
            will need to be updated.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDelete(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteTemplate}
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

export default ConfigTemplate; 