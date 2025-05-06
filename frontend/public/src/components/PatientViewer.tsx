// src/components/PatientViewer.tsx
import React from "react";
import { Typography, Paper, List, ListItem, ListItemText } from "@mui/material";

interface PatientViewerProps {
  patient: any;
}

const PatientViewer: React.FC<PatientViewerProps> = ({ patient }) => {
  if (!patient) {
    return <Typography>Loading patient data...</Typography>;
  }

  return (
    <Paper sx={{ padding: 2, marginBottom: 3 }}>
      <Typography variant="h5" gutterBottom>
        Patient Information
      </Typography>
      <List>
        <ListItem>
          <ListItemText primary="ID" secondary={patient.id} />
        </ListItem>
        {patient.name && patient.name.length > 0 && (
          <ListItem>
            <ListItemText
              primary="Name"
              secondary={\`\${patient.name[0].given?.join(" ") || ""} \${patient.name[0].family || ""}\`}
            />
          </ListItem>
        )}
        {patient.gender && (
          <ListItem>
            <ListItemText primary="Gender" secondary={patient.gender} />
          </ListItem>
        )}
        {patient.birthDate && (
          <ListItem>
            <ListItemText primary="Date of Birth" secondary={patient.birthDate} />
          </ListItem>
        )}
      </List>
    </Paper>
  );
};

export default PatientViewer;
