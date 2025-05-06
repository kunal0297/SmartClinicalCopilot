import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { suggestRules } from '../api';
import type { Rule } from '../api';

export default function Rules() {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    const searchRules = async () => {
      if (searchTerm.length < 2) {
        setSuggestions([]);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const results = await suggestRules(searchTerm);
        setSuggestions(results);
      } catch (err) {
        setError('Failed to fetch rule suggestions');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(searchRules, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  const handleRuleClick = (ruleId: string) => {
    // In a real application, this would fetch the full rule details
    const mockRule: Rule = {
      id: ruleId,
      name: 'Example Rule',
      description: 'This is an example rule',
      conditions: [
        {
          type: 'lab',
          code: 'blood-pressure',
          operator: '>',
          value: 140,
        },
      ],
      actions: [
        {
          type: 'alert',
          message: 'High blood pressure detected',
        },
      ],
      severity: 'high',
    };
    setSelectedRule(mockRule);
    setDialogOpen(true);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Clinical Rules
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Search Rules"
          variant="outlined"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Type to search rules..."
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rule ID</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {suggestions.map((ruleId) => (
                <TableRow key={ruleId}>
                  <TableCell>{ruleId}</TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      onClick={() => handleRuleClick(ruleId)}
                      disabled={loading}
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Rule Details</DialogTitle>
        <DialogContent>
          {selectedRule && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedRule.name}
              </Typography>
              <Typography variant="body1" paragraph>
                {selectedRule.description}
              </Typography>

              <Typography variant="h6" gutterBottom>
                Conditions
              </Typography>
              {selectedRule.conditions.map((condition, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Chip
                    label={`${condition.type.toUpperCase()}`}
                    color="primary"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="body2">
                    {condition.code} {condition.operator} {condition.value}
                  </Typography>
                </Box>
              ))}

              <Typography variant="h6" gutterBottom>
                Actions
              </Typography>
              {selectedRule.actions.map((action, index) => (
                <Box key={index} sx={{ mb: 1 }}>
                  <Chip
                    label={`${action.type.toUpperCase()}`}
                    color="secondary"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="body2">{action.message}</Typography>
                </Box>
              ))}

              <Box sx={{ mt: 2 }}>
                <Chip
                  label={`Severity: ${selectedRule.severity.toUpperCase()}`}
                  color={
                    selectedRule.severity === 'high'
                      ? 'error'
                      : selectedRule.severity === 'medium'
                      ? 'warning'
                      : 'success'
                  }
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 