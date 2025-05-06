// src/components/AlertCard.tsx
import React from "react";
import { Card, CardContent, Typography, Chip } from "@mui/material";

interface AlertCardProps {
  alert: {
    rule_id: string;
    message: string;
    severity?: string;
  };
}

const severityColor = (severity?: string) => {
  switch (severity) {
    case "critical":
      return "error";
    case "warning":
      return "warning";
    case "info":
    default:
      return "info";
  }
};

const AlertCard: React.FC<AlertCardProps> = ({ alert }) => {
  return (
    <Card sx={{ marginBottom: 2 }}>
      <CardContent>
        <Typography variant="h6">{alert.rule_id}</Typography>
        <Typography variant="body1" sx={{ marginBottom: 1 }}>
          {alert.message}
        </Typography>
        <Chip label={alert.severity || "info"} color={severityColor(alert.severity)} />
      </CardContent>
    </Card>
  );
};

export default AlertCard;
