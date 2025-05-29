export interface ConfigValue {
  value: any;
  description: string;
  source: string;
  profile: string;
  environment: string;
  timestamp?: string;
  user?: string;
}

export interface Config {
  id: string;
  name: string;
  description: string;
  type: 'json' | 'yaml' | 'toml' | 'env';
  values: Record<string, ConfigValue>;
  status: string;
  updatedAt: string;
  createdAt?: string;
  error?: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  type: 'json' | 'yaml' | 'toml' | 'env';
  content: string;
  variables: string[];
  tags: string[];
  status: string;
  updatedAt: string;
  createdAt?: string;
  error?: string;
}