// src/components/RuleEditor.tsx
import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";

interface RuleEditorProps {
  onSubmit: (ruleText: string) => void;
}

const RuleEditor: React.FC<RuleEditorProps> = ({ onSubmit }) => {
  const [ruleText, setRuleText] = useState("");

  const handleSubmit = () => {
    if (ruleText.trim().length === 0) return;
    onSubmit(ruleText);
    setRuleText("");
  };

  return (
    <Box sx={{ marginBottom: 3 }}>
      <Typography variant="h6" gutterBottom>
        Enter Custom Rule to Search
      </Typography>
      <TextField
        fullWidth
        multiline
        minRows={3}
        maxRows={6}
        value={ruleText}
        onChange={(e) => setRuleText(e.target.value)}
        placeholder="Type your clinical rule here..."
        sx={{ marginBottom: 2 }}
      />
      <Button variant="contained" onClick={handleSubmit}>
        Search Rule
      </Button>
    </Box>
  );
};

export default RuleEditor;
