import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Chip,
  Divider,
  useTheme
} from '@mui/material';
import {
  Security as SecurityIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Key as KeyIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

interface ConfigSecurityProps {
  open: boolean;
  onClose: () => void;
  onEncrypt: (value: string) => Promise<string>;
  onDecrypt: (value: string) => Promise<string>;
}

const ConfigSecurity: React.FC<ConfigSecurityProps> = ({
  open,
  onClose,
  onEncrypt,
  onDecrypt
}) => {
  const theme = useTheme();
  const [value, setValue] = useState('');
  const [encryptedValue, setEncryptedValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const handleEncrypt = async () => {
    if (!value) return;
    setIsProcessing(true);
    setError(null);
    try {
      const result = await onEncrypt(value);
      setEncryptedValue(result);
    } catch (err) {
      setError('Failed to encrypt value');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDecrypt = async () => {
    if (!encryptedValue) return;
    setIsProcessing(true);
    setError(null);
    try {
      const result = await onDecrypt(encryptedValue);
      setValue(result);
    } catch (err) {
      setError('Failed to decrypt value');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    setValue('');
    setEncryptedValue('');
    setError(null);
  };

  const handleDelete = () => {
    setShowConfirmDelete(true);
  };

  const handleConfirmDelete = () => {
    // Implement delete functionality
    setShowConfirmDelete(false);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
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
          <Typography variant="h6">Configuration Security</Typography>
          <Button onClick={onClose} color="inherit">
            Close
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Encrypt/Decrypt Values
          </Typography>
          <Box display="flex" gap={2}>
            <TextField
              label="Value"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              multiline
              rows={4}
              fullWidth
              variant="outlined"
            />
            <Box display="flex" flexDirection="column" gap={1}>
              <Button
                variant="contained"
                startIcon={isProcessing ? <CircularProgress size={20} /> : <LockIcon />}
                onClick={handleEncrypt}
                disabled={isProcessing || !value}
              >
                Encrypt
              </Button>
              <Button
                variant="outlined"
                startIcon={isProcessing ? <CircularProgress size={20} /> : <LockOpenIcon />}
                onClick={handleDecrypt}
                disabled={isProcessing || !encryptedValue}
              >
                Decrypt
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={handleClear}
                disabled={isProcessing}
              >
                Clear
              </Button>
            </Box>
          </Box>
        </Box>

        {encryptedValue && (
          <Box mb={3}>
            <Typography variant="subtitle1" gutterBottom>
              Encrypted Value
            </Typography>
            <Box
              component="pre"
              sx={{
                p: 2,
                bgcolor: theme.palette.background.default,
                borderRadius: 1,
                overflow: 'auto',
              }}
            >
              {encryptedValue}
            </Box>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Security Information
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary="Encryption Algorithm"
                secondary="AES-256-GCM"
              />
              <ListItemSecondaryAction>
                <Chip label="Secure" color="success" size="small" />
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Key Management"
                secondary="Automatic key rotation every 30 days"
              />
              <ListItemSecondaryAction>
                <Tooltip title="Rotate Key">
                  <IconButton edge="end">
                    <KeyIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Access Control"
                secondary="Role-based access control (RBAC)"
              />
              <ListItemSecondaryAction>
                <Chip label="Enabled" color="primary" size="small" />
              </ListItemSecondaryAction>
            </ListItem>
          </List>
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
            This action cannot be undone. Are you sure you want to delete the
            encryption key?
          </Alert>
          <Typography>
            This will invalidate all encrypted values. You will need to re-encrypt
            all values with a new key.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDelete(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
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

export default ConfigSecurity; 