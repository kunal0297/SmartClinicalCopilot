import { useEffect, useState } from 'react';
import { HoverEffect } from '../components/HoverEffect';
import type { HoverEffectItem } from '../components/HoverEffect';
import { Box, Typography, MenuItem, Select, FormControl, InputLabel, CircularProgress } from '@mui/material';

const resourceTypes = [
  'Patient',
  'Observation',
  'Condition',
  'MedicationRequest',
];

export default function FHIRResourceExplorer() {
  const [resourceType, setResourceType] = useState('Patient');
  const [items, setItems] = useState<HoverEffectItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`/fhir-explorer/${resourceType}?count=12`)
      .then((res) => res.json())
      .then((data) => {
        setItems(
          (data.resources || []).map((r: any) => ({
            title: r.name?.[0]?.text || r.code?.text || r.id || 'Resource',
            description:
              r.resourceType === 'Patient'
                ? `Gender: ${r.gender || 'N/A'}, BirthDate: ${r.birthDate || 'N/A'}`
                : r.resourceType === 'Observation'
                ? `Value: ${r.valueQuantity?.value || 'N/A'} ${r.valueQuantity?.unit || ''}`
                : r.resourceType === 'Condition'
                ? `Status: ${r.clinicalStatus?.coding?.[0]?.code || 'N/A'}`
                : r.resourceType === 'MedicationRequest'
                ? `Status: ${r.status || 'N/A'}`
                : 'FHIR Resource',
            link: undefined,
          }))
        );
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [resourceType]);

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, mx: 'auto', py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold', textAlign: 'center' }}>
        FHIR Resource Explorer
      </Typography>
      <FormControl sx={{ mb: 4, minWidth: 200 }}>
        <InputLabel>Resource Type</InputLabel>
        <Select
          value={resourceType}
          label="Resource Type"
          onChange={(e) => setResourceType(e.target.value as string)}
        >
          {resourceTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <HoverEffect items={items} />
      )}
    </Box>
  );
} 