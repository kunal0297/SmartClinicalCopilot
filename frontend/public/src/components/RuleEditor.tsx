// src/components/RuleEditor.tsx
import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";

interface RuleEditorProps {
  onSubmit: (ruleText: string) => void;
}

const RuleEditor: React.FC<RuleEditorProps> = ({ onSubmit }) => {
  const [ruleText, setRuleText] = useState("");

  const handleSubmit = () => {
    const trimmedRule = ruleText.trim();
    if (!trimmedRule) return;
    onSubmit(trimmedRule);
    setRuleText("");
  };

  return (
    <Box sx={{ mb: 3 }}>
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
        sx={{ mb: 2 }}
      />
      <Button variant="contained" onClick={handleSubmit}>
        Search Rule
      </Button>
    </Box>
  );
};

export default RuleEditor;
