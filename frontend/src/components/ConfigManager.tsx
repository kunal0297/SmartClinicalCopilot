import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import type { Config, Template } from '../types/config';
import ConfigEditor from './ConfigEditor';
import ConfigSecurity from './ConfigSecurity';
import ConfigTemplate from './ConfigTemplate';
import ConfigValidation from './ConfigValidation';
import ConfigStats from './ConfigStats';

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

interface ConfigManagerProps {
  onSaveConfig: (config: Config) => Promise<void>;
  onEncrypt: (value: string) => Promise<string>;
  onDecrypt: (value: string) => Promise<string>;
  onSaveTemplate: (template: Template) => Promise<void>;
  onDeleteTemplate: (templateId: string) => Promise<void>;
  onApplyTemplate: (templateId: string, variables: Record<string, string>) => Promise<any>;
  onValidate: (config: Config) => Promise<ValidationResult[]>;
  onSaveRule: (rule: ValidationRule) => Promise<void>;
  onDeleteRule: (ruleId: string) => Promise<void>;
  configs: Config[];
  templates: Template[];
  rules: ValidationRule[];
  results: ValidationResult[];
}

const ConfigManager: React.FC<ConfigManagerProps> = ({
  onSaveConfig,
  onEncrypt,
  onDecrypt,
  onSaveTemplate,
  onDeleteTemplate,
  onApplyTemplate,
  onValidate,
  onSaveRule,
  onDeleteRule,
  configs,
  templates,
  rules,
  results
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedConfig, setSelectedConfig] = useState<Config | null>(null);
  const [validationRules, setValidationRules] = useState<ValidationRule[]>(rules);
  const [validationResults, setValidationResults] = useState<ValidationResult[]>(results);

  useEffect(() => {
    if (configs.length > 0) {
      setSelectedConfig(configs[0]);
    }
  }, [configs]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSaveConfig = async (config: Config) => {
    setLoading(true);
    setError(null);
    try {
      await onSaveConfig(config);
      setSelectedConfig(config);
    } catch (err) {
      setError('Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (config: Config): Promise<ValidationResult[]> => {
    setLoading(true);
    setError(null);
    try {
      const result = await onValidate(config);
      setValidationResults(result);
      return result;
    } catch (err) {
      setError('Failed to validate configuration');
      return [];
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRule = async (rule: ValidationRule) => {
    setLoading(true);
    setError(null);
    try {
      await onSaveRule(rule);
      setValidationRules([...validationRules, rule]);
    } catch (err) {
      setError('Failed to save validation rule');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    setLoading(true);
    setError(null);
    try {
      await onDeleteRule(ruleId);
      setValidationRules(validationRules.filter(rule => rule.id !== ruleId));
    } catch (err) {
      setError('Failed to delete validation rule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Paper sx={{ mb: 2 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Editor" />
          <Tab label="Security" />
          <Tab label="Templates" />
          <Tab label="Validation" />
          <Tab label="Stats" />
        </Tabs>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box display="flex" justifyContent="center" my={2}>
          <CircularProgress />
        </Box>
      )}

      {activeTab === 0 && selectedConfig && (
        <ConfigEditor
          config={selectedConfig}
          onSave={handleSaveConfig}
        />
      )}

      {activeTab === 1 && selectedConfig && (
        <ConfigSecurity
          config={selectedConfig}
          onClose={() => setActiveTab(0)}
          onEncrypt={onEncrypt}
          onDecrypt={onDecrypt}
        />
      )}

      {activeTab === 2 && (
        <ConfigTemplate
          open={true}
          onClose={() => setActiveTab(0)}
          onSaveTemplate={onSaveTemplate as (template: Template) => Promise<void>}
          onDeleteTemplate={onDeleteTemplate}
          onApplyTemplate={onApplyTemplate}
          templates={templates.map(t => ({
            ...t,
            status: t.status || 'active',
            createdAt: t.createdAt || new Date().toISOString(),
            updatedAt: t.updatedAt || new Date().toISOString()
          }))}
        />
      )}

      {activeTab === 3 && selectedConfig && (
        <ConfigValidation
          open={true}
          onClose={() => setActiveTab(0)}
          onValidate={() => handleValidate(selectedConfig)}
          onSaveRule={handleSaveRule}
          onDeleteRule={handleDeleteRule}
          rules={validationRules}
          results={validationResults}
        />
      )}

      {activeTab === 4 && selectedConfig && (
        <ConfigStats
          open={true}
          onClose={() => setActiveTab(0)}
          stats={{
            totalConfigs: configs.length,
            activeConfigs: configs.filter(c => c.status === 'active').length,
            encryptedConfigs: configs.filter(c => c.status === 'encrypted').length,
            lastUpdated: selectedConfig.updatedAt || new Date().toISOString(),
            accessCount: 0,
            errorCount: 0,
            avgResponseTime: 0,
            cacheHitRate: 0,
            memoryUsage: 0,
            diskUsage: 0,
            operationHistory: [],
            errorDistribution: [],
            accessPatterns: []
          }}
        />
      )}
    </Box>
  );
};

export default ConfigManager;