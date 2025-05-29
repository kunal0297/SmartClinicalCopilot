import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert
} from '@mui/material';
import {
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import type { Config } from '../types/config';

interface ConfigSecurityProps {
  config: Config | null;
  onClose: () => void;
  onEncrypt: (value: string) => Promise<string>;
  onDecrypt: (value: string) => Promise<string>;
}

const ConfigSecurity: React.FC<ConfigSecurityProps> = ({
  config,
  onClose,
  onEncrypt,
  onDecrypt
}) => {
  const [encryptionKey, setEncryptionKey] = React.useState('');
  const [isEncrypted, setIsEncrypted] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleEncrypt = async () => {
    if (encryptionKey && config) {
      try {
        const encryptedValue = await onEncrypt(encryptionKey);
        setIsEncrypted(true);
        console.log('Encrypted value:', encryptedValue);
      } catch (err) {
        setError('Failed to encrypt configuration');
      }
    }
  };

  const handleDecrypt = async () => {
    if (encryptionKey && config) {
      try {
        const decryptedValue = await onDecrypt(encryptionKey);
        setIsEncrypted(false);
        console.log('Decrypted value:', decryptedValue);
      } catch (err) {
        setError('Failed to decrypt configuration');
      }
    }
  };

  return (
    <Dialog open={true} maxWidth="sm" fullWidth>
      <DialogTitle>Configuration Security</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Typography variant="subtitle1" gutterBottom>
            Configuration: {config?.name || 'No configuration selected'}
          </Typography>
          <Typography variant="subtitle1" gutterBottom>
            Encryption Status: {isEncrypted ? 'Encrypted' : 'Not Encrypted'}
          </Typography>
          <TextField
            fullWidth
            label="Encryption Key"
            type="password"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
            margin="normal"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleDecrypt} disabled={!isEncrypted}>
          <LockOpenIcon /> Decrypt
        </Button>
        <Button onClick={handleEncrypt} disabled={isEncrypted}>
          <LockIcon /> Encrypt
        </Button>
        <Button onClick={onClose}>
          <RefreshIcon /> Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfigSecurity;