// src/components/PatientViewer.tsx
import React from "react";
import { Typography, Paper, List, ListItem, ListItemText } from "@mui/material";

interface HumanName {
  given?: string[];
  family?: string;
}

interface Patient {
  id: string;
  name?: HumanName[];
  gender?: string;
  birthDate?: string;
}

interface PatientViewerProps {
  patient?: Patient;
}

const PatientViewer: React.FC<PatientViewerProps> = ({ patient }) => {
  if (!patient) {
    return <Typography>Loading patient data...</Typography>;
  }

  const { id, name, gender, birthDate } = patient;
  const fullName = name?.[0]
    ? `${name[0].given?.join(" ") || ""} ${name[0].family || ""}`.trim()
    : undefined;

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Patient Information
      </Typography>
      <List>
        <ListItem>
          <ListItemText primary="ID" secondary={id} />
        </ListItem>
        {fullName && (
          <ListItem>
            <ListItemText primary="Name" secondary={fullName} />
          </ListItem>
        )}
        {gender && (
          <ListItem>
            <ListItemText primary="Gender" secondary={gender} />
          </ListItem>
        )}
        {birthDate && (
          <ListItem>
            <ListItemText primary="Date of Birth" secondary={birthDate} />
          </ListItem>
        )}
      </List>
    </Paper>
  );
};

export default PatientViewer;
