import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Tooltip,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  useTheme,
  Button,
  Divider,
  Chip
} from '@mui/material';
import {
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Code as CodeIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import type { Config } from '../types/config';

interface ConfigEditorProps {
  config: Config;
  onSave: (config: Config) => Promise<void>;
}

const ConfigEditor: React.FC<ConfigEditorProps> = ({ config, onSave }) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showValue, setShowValue] = useState<Record<string, boolean>>({});
  const [editorValue, setEditorValue] = useState('');

  const filteredKeys = Object.keys(config.values).filter(key =>
    key.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleKeySelect = (key: string) => {
    setSelectedKey(key);
    setEditorValue(JSON.stringify(config.values[key].value, null, 2));
  };

  const handleToggleVisibility = (key: string) => {
    setShowValue(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleValueChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorValue(value);
    }
  };

  const handleSave = async () => {
    if (selectedKey) {
      try {
        const parsedValue = JSON.parse(editorValue);
        const updatedConfig = {
          ...config,
          values: {
            ...config.values,
            [selectedKey]: {
              ...config.values[selectedKey],
              value: parsedValue
            }
          }
        };
        await onSave(updatedConfig);
        setIsEditing(false);
      } catch (error) {
        console.error('Invalid JSON:', error);
      }
    }
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <Paper>
          <Box mb={2}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search configuration..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
            />
          </Box>
          <List>
            {filteredKeys.map((key) => (
              <ListItem
                key={key}
                button
                selected={selectedKey === key}
                onClick={() => handleKeySelect(key)}
              >
                <ListItemText
                  primary={key}
                  secondary={config.values[key].description || 'No description available'}
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Toggle visibility">
                    <IconButton
                      edge="end"
                      onClick={() => handleToggleVisibility(key)}
                    >
                      {showValue[key] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12} md={8}>
        <Paper>
          {selectedKey ? (
            <>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">{selectedKey}</Typography>
                <Box>
                  <Tooltip title="Edit">
                    <IconButton
                      onClick={() => setIsEditing(!isEditing)}
                      color={isEditing ? 'primary' : 'default'}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="View as JSON">
                    <IconButton>
                      <CodeIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Security">
                    <IconButton>
                      <SecurityIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  {config.values[selectedKey].description || 'No description available'}
                </Typography>
              </Box>
              <Box mb={2}>
                <Chip
                  label={`Source: ${config.values[selectedKey].source}`}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`Profile: ${config.values[selectedKey].profile}`}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`Environment: ${config.values[selectedKey].environment}`}
                  size="small"
                />
              </Box>
              <Divider sx={{ my: 2 }} />
              {isEditing ? (
                <Box>
                  <Editor
                    height="400px"
                    language="json"
                    theme={theme.palette.mode === 'dark' ? 'vs-dark' : 'light'}
                    value={editorValue}
                    onChange={handleValueChange}
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      wordWrap: 'on',
                      automaticLayout: true,
                    }}
                  />
                  <Box mt={2} display="flex" justifyContent="flex-end">
                    <Button
                      variant="outlined"
                      onClick={() => setIsEditing(false)}
                      sx={{ mr: 1 }}
                    >
                      Cancel
                    </Button>
                    <Button variant="contained" onClick={handleSave}>
                      Save
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box>
                  <Typography variant="body1">
                    {showValue[selectedKey]
                      ? JSON.stringify(config.values[selectedKey].value, null, 2)
                      : '••••••••'}
                  </Typography>
                </Box>
              )}
            </>
          ) : (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              minHeight="400px"
            >
              <Typography variant="body1" color="textSecondary">
                Select a configuration key to view or edit
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ConfigEditor;