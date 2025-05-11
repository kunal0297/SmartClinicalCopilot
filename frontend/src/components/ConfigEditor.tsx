import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Tooltip,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { ConfigValue } from '../types/config';
import MonacoEditor from '@monaco-editor/react';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[2],
  '&:hover': {
    boxShadow: theme.shadows[4],
  },
}));

interface ConfigEditorProps {
  config: any;
  onSave: () => void;
  onRefresh: () => void;
}

const ConfigEditor: React.FC<ConfigEditorProps> = ({ config, onSave, onRefresh }) => {
  const theme = useTheme();
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showValue, setShowValue] = useState<Record<string, boolean>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [editorValue, setEditorValue] = useState('');

  const handleKeySelect = (key: string) => {
    setSelectedKey(key);
    setEditorValue(JSON.stringify(config.values[key], null, 2));
  };

  const handleValueChange = (value: string) => {
    setEditorValue(value);
  };

  const handleSave = () => {
    try {
      const newValue = JSON.parse(editorValue);
      // Update config value
      onSave();
      setIsEditing(false);
    } catch (error) {
      // Handle JSON parse error
    }
  };

  const handleToggleVisibility = (key: string) => {
    setShowValue((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const filteredKeys = Object.keys(config.values).filter((key) =>
    key.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <StyledPaper>
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
                  secondary={
                    config.values[key].description || 'No description available'
                  }
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
        </StyledPaper>
      </Grid>
      <Grid item xs={12} md={8}>
        <StyledPaper>
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
                  <MonacoEditor
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
        </StyledPaper>
      </Grid>
    </Grid>
  );
};

export default ConfigEditor; 