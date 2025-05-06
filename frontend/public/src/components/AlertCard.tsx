// src/components/AlertCard.tsx
import React from "react";
import { Card, CardContent, Typography, Chip } from "@mui/material";

type Severity = "critical" | "warning" | "info" | undefined;

interface Alert {
  rule_id: string;
  message: string;
  severity?: Severity;
}

interface AlertCardProps {
  alert: Alert;
}

const getSeverityColor = (severity: Severity = "info") => {
  switch (severity) {
    case "critical":
      return "error";
    case "warning":
      return "warning";
    default:
      return "info";
  }
};

const AlertCard: React.FC<AlertCardProps> = ({ alert }) => {
  const { rule_id, message, severity = "info" } = alert;

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {rule_id}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          {message}
        </Typography>
        <Chip label={severity} color={getSeverityColor(severity)} />
      </CardContent>
    </Card>
  );
};

export default AlertCard;
