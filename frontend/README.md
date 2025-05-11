# Smart Clinical Copilot - Frontend

The frontend application for the Smart Clinical Copilot configuration management system. Built with React, TypeScript, and Material-UI, this application provides a modern and intuitive interface for managing application configurations.

## Features

### User Interface
- Modern, responsive design
- Intuitive configuration management
- Real-time validation feedback
- Rich text editing with Monaco Editor
- Interactive data visualization
- Dark/Light theme support

### Configuration Management
- Configuration editor with syntax highlighting
- Template management
- Validation rules editor
- Import/Export functionality
- Configuration history
- Backup and restore

### Security
- Encryption/Decryption interface
- Access control management
- Audit logging viewer
- Security statistics

### Performance
- Optimized rendering
- Efficient state management
- Caching strategies
- Lazy loading
- Code splitting

## Technology Stack

- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Component library
- **Monaco Editor**: Code editor
- **Recharts**: Data visualization
- **React Query**: Data fetching
- **Redux Toolkit**: State management
- **Axios**: HTTP client
- **Jest**: Testing framework
- **Cypress**: E2E testing

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── assets/
├── src/
│   ├── components/
│   │   ├── ConfigEditor/
│   │   ├── ConfigSecurity/
│   │   ├── ConfigTemplate/
│   │   ├── ConfigValidation/
│   │   ├── ConfigImportExport/
│   │   └── ConfigStats/
│   ├── hooks/
│   │   ├── useConfig.ts
│   │   ├── useAuth.ts
│   │   └── useTheme.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── config.ts
│   │   └── auth.ts
│   ├── store/
│   │   ├── slices/
│   │   └── index.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   └── formatting.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm start
```

### Development

1. **Running Tests**
```bash
# Unit tests
npm test

# E2E tests
npm run cypress
```

2. **Building for Production**
```bash
npm run build
```

3. **Code Quality**
```bash
# Linting
npm run lint

# Type checking
npm run type-check
```

## Component Documentation

### ConfigEditor
The main configuration editor component that provides a rich interface for editing configuration values.

```typescript
interface ConfigEditorProps {
  configs: Config[];
  onSave: (config: Config) => Promise<void>;
  onRefresh: () => void;
}
```

### ConfigSecurity
Component for managing encryption and security settings.

```typescript
interface ConfigSecurityProps {
  open: boolean;
  onClose: () => void;
  onEncrypt: (value: string) => Promise<string>;
  onDecrypt: (value: string) => Promise<string>;
}
```

### ConfigTemplate
Component for managing configuration templates.

```typescript
interface ConfigTemplateProps {
  open: boolean;
  onClose: () => void;
  onSaveTemplate: (template: Template) => Promise<void>;
  onDeleteTemplate: (templateId: string) => Promise<void>;
  onApplyTemplate: (templateId: string, variables: Record<string, string>) => Promise<any>;
  templates: Template[];
}
```

### ConfigValidation
Component for managing validation rules and running validations.

```typescript
interface ConfigValidationProps {
  open: boolean;
  onClose: () => void;
  onValidate: (config: any) => Promise<any>;
  onSaveRule: (rule: Rule) => Promise<void>;
  onDeleteRule: (ruleId: string) => Promise<void>;
  rules: Rule[];
  results: ValidationResult[];
}
```

### ConfigImportExport
Component for importing and exporting configurations.

```typescript
interface ConfigImportExportProps {
  open: boolean;
  onClose: () => void;
  onImport: (file: File) => Promise<void>;
  onExport: (config: any) => Promise<void>;
  onDelete: (configId: string) => Promise<void>;
  configs: Config[];
}
```

### ConfigStats
Component for displaying configuration statistics and metrics.

```typescript
interface ConfigStatsProps {
  open: boolean;
  onClose: () => void;
  stats: Stats;
}
```

## State Management

The application uses Redux Toolkit for state management. The main slices include:

- **config**: Configuration state
- **auth**: Authentication state
- **ui**: UI state (theme, loading, etc.)

## API Integration

The frontend communicates with the backend through a RESTful API. The main API endpoints are:

- `/api/config`: Configuration management
- `/api/templates`: Template management
- `/api/validation`: Validation rules
- `/api/security`: Security operations
- `/api/stats`: Statistics and metrics

## Styling

The application uses Material-UI's styling solution with custom theme configuration. The theme can be customized in `src/theme/index.ts`.

## Testing

### Unit Tests
- Jest for unit testing
- React Testing Library for component testing
- Mock Service Worker for API mocking

### E2E Tests
- Cypress for end-to-end testing
- Custom commands for common operations
- Visual regression testing

## Performance Optimization

1. **Code Splitting**
   - Route-based code splitting
   - Component lazy loading
   - Dynamic imports

2. **Caching**
   - React Query for data caching
   - Local storage for user preferences
   - Service worker for offline support

3. **Bundle Optimization**
   - Tree shaking
   - Code minification
   - Asset optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
