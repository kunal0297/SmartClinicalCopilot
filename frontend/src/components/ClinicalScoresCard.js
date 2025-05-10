import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Divider,
  CircularProgress
} from '@mui/material';
import { Assessment as AssessmentIcon } from '@mui/icons-material';

function ClinicalScoresCard({ scores, onCalculate }) {
  const renderScore = (scoreType, score) => {
    if (!score) return null;

    return (
      <Box key={scoreType} sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {scoreType}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4" color="primary" sx={{ mr: 2 }}>
            {score.score_value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {score.interpretation}
          </Typography>
        </Box>
        {score.details && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Details:
            </Typography>
            {Object.entries(score.details).map(([key, value]) => (
              <Typography key={key} variant="body2" color="text.secondary">
                {key}: {value}
              </Typography>
            ))}
          </Box>
        )}
        <Divider sx={{ my: 1 }} />
      </Box>
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Clinical Scores
        </Typography>
        <Box sx={{ mt: 2 }}>
          {Object.entries(scores).map(([type, score]) => renderScore(type, score))}
          {Object.keys(scores).length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No clinical scores calculated yet
            </Typography>
          )}
        </Box>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          startIcon={<AssessmentIcon />}
          onClick={() => onCalculate('CHA2DS2-VASc')}
        >
          Calculate CHA₂DS₂-VASc
        </Button>
        <Button
          size="small"
          startIcon={<AssessmentIcon />}
          onClick={() => onCalculate('Wells')}
        >
          Calculate Wells
        </Button>
      </CardActions>
    </Card>
  );
}

export default ClinicalScoresCard; 