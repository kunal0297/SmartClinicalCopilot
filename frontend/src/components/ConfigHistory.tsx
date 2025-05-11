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
  useTheme
} from '@mui/material';
import {
  Restore as RestoreIcon,
  Visibility as VisibilityIcon,
  Compare as CompareIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

interface ConfigHistoryProps {
  open: boolean;
  onClose: () => void;
  history: Array<{
    key: string;
    value: any;
    timestamp: string;
    user: string;
    action: string;
  }>;
}

const ConfigHistory: React.FC<ConfigHistoryProps> = ({ open, onClose, history }) => {
  const theme = useTheme();
  const [selectedEntry, setSelectedEntry] = useState<any>(null);
  const [showDiff, setShowDiff] = useState(false);

  const handleRestore = (entry: any) => {
    // Implement restore functionality
  };

  const handleCompare = (entry: any) => {
    setSelectedEntry(entry);
    setShowDiff(true);
  };

  const handleDelete = (entry: any) => {
    // Implement delete functionality
  };

  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'success';
      case 'update':
        return 'primary';
      case 'delete':
        return 'error';
      default:
        return 'default';
    }
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
          <Typography variant="h6">Configuration History</Typography>
          <Button onClick={onClose} color="inherit">
            Close
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <List>
          {history.map((entry, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1">{entry.key}</Typography>
                      <Chip
                        label={entry.action}
                        size="small"
                        color={getActionColor(entry.action)}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="textSecondary">
                        {format(new Date(entry.timestamp), 'PPpp')}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        By: {entry.user}
                      </Typography>
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title="View">
                    <IconButton edge="end" onClick={() => handleCompare(entry)}>
                      <VisibilityIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Compare">
                    <IconButton edge="end" onClick={() => handleCompare(entry)}>
                      <CompareIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Restore">
                    <IconButton edge="end" onClick={() => handleRestore(entry)}>
                      <RestoreIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton edge="end" onClick={() => handleDelete(entry)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
              {index < history.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Diff Dialog */}
      <Dialog
        open={showDiff}
        onClose={() => setShowDiff(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Compare Changes</DialogTitle>
        <DialogContent dividers>
          {selectedEntry && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Changes made by {selectedEntry.user} on{' '}
                {format(new Date(selectedEntry.timestamp), 'PPpp')}
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
                {JSON.stringify(selectedEntry.value, null, 2)}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDiff(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default ConfigHistory; 