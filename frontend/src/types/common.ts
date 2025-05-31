import type { ReactNode } from 'react';

// Common component props
export interface BaseProps {
  className?: string;
  children?: ReactNode;
}

// Chart related types
export interface ChartDataPoint {
  name: string;
  value?: number;
  [key: string]: any;
}

export interface ChartProps extends BaseProps {
  data: ChartDataPoint[];
  width?: number;
  height?: number;
}

// Alert related types
export interface Alert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: Date;
  source: string;
}

// Configuration related types
export interface ConfigItem {
  id: string;
  name: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'object';
  description?: string;
  required?: boolean;
}

// Clinical related types
export interface ClinicalScore {
  id: string;
  patientId: string;
  score: number;
  type: string;
  timestamp: Date;
  details?: Record<string, any>;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  error?: string;
}

// Form related types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'date';
  required?: boolean;
  options?: Array<{ label: string; value: string | number }>;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    custom?: (value: any) => boolean;
  };
}

// Navigation types
export interface NavItem {
  label: string;
  path: string;
  icon?: React.ComponentType;
  children?: NavItem[];
}

// Theme types
export interface Theme {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  background: string;
  text: string;
} 