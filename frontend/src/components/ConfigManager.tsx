import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  IconButton,
  Tooltip,
  useTheme,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Description as DescriptionIcon,
  FileUpload as FileUploadIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import ConfigEditor from './ConfigEditor';
import ConfigSecurity from './ConfigSecurity';
import ConfigTemplate from './ConfigTemplate';
import ConfigValidation from './ConfigValidation';
import ConfigImportExport from './ConfigImportExport';
import ConfigStats from './ConfigStats';

interface ConfigManagerProps {
  onSave: (config: any) => Promise<void>;
  onLoad: () => Promise<any>;
  onValidate: (config: any) => Promise<any>;
  onEncrypt: (value: string) => Promise<string>;
  onDecrypt: (value: string) => Promise<string>;
  onImport: (file: File) => Promise<void>;
  onExport: (config: any) => Promise<void>;
  onDelete: (configId: string) => Promise<void>;
  onSaveTemplate: (template: any) => Promise<void>;
  onDeleteTemplate: (templateId: string) => Promise<void>;
  onApplyTemplate: (templateId: string, variables: Record<string, string>) => Promise<any>;
  onSaveRule: (rule: any) => Promise<void>;
  onDeleteRule: (ruleId: string) => Promise<void>;
  configs: any[];
  templates: any[];
  rules: any[];
  stats: any;
}

const ConfigManager: React.FC<ConfigManagerProps> = ({
  onSave,
  onLoad,
  onValidate,
  onEncrypt,
  onDecrypt,
  onImport,
  onExport,
  onDelete,
  onSaveTemplate,
  onDeleteTemplate,
  onApplyTemplate,
  onSaveRule,
  onDeleteRule,
  configs,
  templates,
  rules,
  stats
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSecurity, setShowSecurity] = useState(false);
  const [showTemplate, setShowTemplate] = useState(false);
  const [showValidation, setShowValidation] = useState(false);
  const [showImportExport, setShowImportExport] = useState(false);
  const [showStats, setShowStats] = useState(false);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await onLoad();
    } catch (err) {
      setError('Failed to load configurations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <SettingsIcon color="action" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Configuration Manager</Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={loadConfigs} disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setActiveTab(0)}
          >
            New Configuration
          </Button>
        </Box>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid component="div" item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage encryption and access control
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  startIcon={<SecurityIcon />}
                  onClick={() => setShowSecurity(true)}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid component="div" item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Templates
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create and manage configuration templates
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  startIcon={<DescriptionIcon />}
                  onClick={() => setShowTemplate(true)}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid component="div" item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Import/Export
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Import and export configurations
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  startIcon={<FileUploadIcon />}
                  onClick={() => setShowImportExport(true)}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid component="div" item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statistics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View configuration statistics
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  startIcon={<AssessmentIcon />}
                  onClick={() => setShowStats(true)}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Main Content */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Editor" />
          <Tab label="Validation" />
          <Tab label="History" />
        </Tabs>
        <Box sx={{ p: 2 }}>
          {activeTab === 0 && (
            <ConfigEditor
              configs={configs}
              onSave={(config) => onSave(config)}
              onRefresh={loadConfigs}
            />
          )}
          {activeTab === 1 && (
            <ConfigValidation
              open={true}
              onClose={() => setActiveTab(0)}
              onValidate={onValidate}
              onSaveRule={onSaveRule}
              onDeleteRule={onDeleteRule}
              rules={rules}
              results={[]}
            />
          )}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Configuration History
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
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.secondary"
                              display="block"
                            >
                              Last updated: {config.updatedAt}
                            </Typography>
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
                          <IconButton edge="end">
                            <EditIcon />
                          </IconButton>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Dialogs */}
      <ConfigSecurity
        open={showSecurity}
        onClose={() => setShowSecurity(false)}
        onEncrypt={onEncrypt}
        onDecrypt={onDecrypt}
      />
      <ConfigTemplate
        open={showTemplate}
        onClose={() => setShowTemplate(false)}
        onSaveTemplate={onSaveTemplate}
        onDeleteTemplate={onDeleteTemplate}
        onApplyTemplate={onApplyTemplate}
        templates={templates}
      />
      <ConfigImportExport
        open={showImportExport}
        onClose={() => setShowImportExport(false)}
        onImport={onImport}
        onExport={onExport}
        onDelete={onDelete}
        configs={configs}
      />
      <ConfigStats
        open={showStats}
        onClose={() => setShowStats(false)}
        stats={stats}
      />
    </Box>
  );
};

export default ConfigManager; 