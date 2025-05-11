import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Box,
  Chip,
  Divider,
  Tooltip,
  TextField,
  Alert,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  Backup as BackupIcon,
  Restore as RestoreIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

interface ConfigBackupProps {
  open: boolean;
  onClose: () => void;
  onBackup: () => void;
  onRestore: (backupName: string) => void;
  backups: Array<{
    name: string;
    timestamp: string;
    size: number;
    description?: string;
    type: 'manual' | 'automatic';
  }>;
}

const ConfigBackup: React.FC<ConfigBackupProps> = ({
  open,
  onClose,
  onBackup,
  onRestore,
  backups
}) => {
  const theme = useTheme();
  const [backupName, setBackupName] = useState('');
  const [backupDescription, setBackupDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<string | null>(null);
  const [showConfirmRestore, setShowConfirmRestore] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const handleCreateBackup = async () => {
    setIsCreating(true);
    try {
      await onBackup();
      setBackupName('');
      setBackupDescription('');
    } finally {
      setIsCreating(false);
    }
  };

  const handleRestore = async (backupName: string) => {
    setSelectedBackup(backupName);
    setShowConfirmRestore(true);
  };

  const handleConfirmRestore = async () => {
    if (selectedBackup) {
      await onRestore(selectedBackup);
      setShowConfirmRestore(false);
      setSelectedBackup(null);
    }
  };

  const handleDelete = (backupName: string) => {
    setSelectedBackup(backupName);
    setShowConfirmDelete(true);
  };

  const handleConfirmDelete = async () => {
    // Implement delete functionality
    setShowConfirmDelete(false);
    setSelectedBackup(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
          <Typography variant="h6">Configuration Backups</Typography>
          <Button onClick={onClose} color="inherit">
            Close
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Create New Backup
          </Typography>
          <Box display="flex" gap={2}>
            <TextField
              label="Backup Name"
              value={backupName}
              onChange={(e) => setBackupName(e.target.value)}
              size="small"
              fullWidth
            />
            <TextField
              label="Description"
              value={backupDescription}
              onChange={(e) => setBackupDescription(e.target.value)}
              size="small"
              fullWidth
            />
            <Button
              variant="contained"
              startIcon={isCreating ? <CircularProgress size={20} /> : <BackupIcon />}
              onClick={handleCreateBackup}
              disabled={isCreating || !backupName}
            >
              {isCreating ? 'Creating...' : 'Create Backup'}
            </Button>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle1" gutterBottom>
          Available Backups
        </Typography>
        <List>
          {backups.map((backup, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1">{backup.name}</Typography>
                      <Chip
                        label={backup.type}
                        size="small"
                        color={backup.type === 'manual' ? 'primary' : 'secondary'}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="textSecondary">
                        {format(new Date(backup.timestamp), 'PPpp')}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Size: {formatFileSize(backup.size)}
                      </Typography>
                      {backup.description && (
                        <Typography variant="body2" color="textSecondary">
                          {backup.description}
                        </Typography>
                      )}
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Download">
                    <IconButton edge="end">
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Restore">
                    <IconButton
                      edge="end"
                      onClick={() => handleRestore(backup.name)}
                    >
                      <RestoreIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      edge="end"
                      onClick={() => handleDelete(backup.name)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
              {index < backups.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Confirm Restore Dialog */}
      <Dialog
        open={showConfirmRestore}
        onClose={() => setShowConfirmRestore(false)}
      >
        <DialogTitle>Confirm Restore</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will overwrite your current configuration. Are you sure you want to
            proceed?
          </Alert>
          <Typography>
            You are about to restore backup: {selectedBackup}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmRestore(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmRestore}
            color="primary"
            variant="contained"
          >
            Restore
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirm Delete Dialog */}
      <Dialog
        open={showConfirmDelete}
        onClose={() => setShowConfirmDelete(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This action cannot be undone. Are you sure you want to delete this
            backup?
          </Alert>
          <Typography>
            You are about to delete backup: {selectedBackup}
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

export default ConfigBackup; 