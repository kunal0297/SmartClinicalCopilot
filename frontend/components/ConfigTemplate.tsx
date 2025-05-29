// Remove local interface
// interface Template {
//   id: string;
//   name: string;
//   description: string;
//   status: string;
//   createdAt: string;
//   updatedAt: string;
// }

// Update to use imported type
import { Template } from '../types/config';

// Ensure required fields are present
const templates: Template[] = [
  {
    id: '1',
    name: 'Template 1',
    description: 'Description 1',
    status: 'Active',
    createdAt: '2023-01-01',
    updatedAt: '2023-01-01',
  },
  // ... other templates
]; 