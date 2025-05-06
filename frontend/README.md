# SmartClinicalCopilot Frontend 🎨

A modern, responsive frontend for the SmartClinicalCopilot system, built with React and TypeScript.

## ✨ Features

### 1. Clinical Dashboard
- Real-time patient data display
- Interactive rule matching interface
- Alert prioritization and filtering
- Clinical context visualization

### 2. Rule Management
- Rule search with autocomplete
- Rule validation and testing
- Rule performance metrics
- Rule feedback tracking

### 3. Alert Interface
- Severity-based alert display
- Natural language explanations
- Evidence-based recommendations
- Clinical guideline references

### 4. Feedback System
- Alert helpfulness rating
- Rule-specific feedback
- Historical feedback analysis
- Performance metrics

## 🛠️ Technical Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Material-UI
- **State Management**: Redux Toolkit
- **API Client**: Axios
- **Testing**: Jest + React Testing Library
- **Build Tool**: Vite

## 📦 Dependencies

```json
{
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/material": "^5.13.0",
    "@reduxjs/toolkit": "^1.9.5",
    "axios": "^1.4.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^8.0.5",
    "react-router-dom": "^6.11.1"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^14.0.0",
    "@types/react": "^18.2.6",
    "@types/react-dom": "^18.2.4",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.4",
    "vite": "^4.3.5"
  }
}
```

## 🔧 Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
# .env
VITE_API_URL=http://localhost:8000
VITE_ENV=development
```

3. Start development server:
```bash
npm run dev
```

## 📱 UI Components

### 1. Patient Dashboard
```tsx
<PatientDashboard
  patientId={id}
  onAlertSelect={handleAlertSelect}
  onFeedbackSubmit={handleFeedback}
/>
```

### 2. Alert Display
```tsx
<AlertCard
  alert={alert}
  onFeedback={handleFeedback}
  onExplain={handleExplain}
/>
```

### 3. Rule Search
```tsx
<RuleSearch
  onSearch={handleSearch}
  onSelect={handleSelect}
  suggestions={suggestions}
/>
```

### 4. Feedback Form
```tsx
<FeedbackForm
  alertId={alertId}
  ruleId={ruleId}
  onSubmit={handleSubmit}
/>
```

## 🎨 UI/UX Features

1. **Responsive Design**
   - Mobile-first approach
   - Adaptive layouts
   - Touch-friendly interfaces

2. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Screen reader support

3. **Performance**
   - Code splitting
   - Lazy loading
   - Memoization

4. **User Experience**
   - Real-time updates
   - Smooth animations
   - Error handling
   - Loading states

## 📊 State Management

```typescript
// Store configuration
const store = configureStore({
  reducer: {
    alerts: alertsReducer,
    rules: rulesReducer,
    feedback: feedbackReducer,
    ui: uiReducer
  }
});

// Slice example
const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    setAlerts: (state, action) => {
      state.items = action.payload;
    },
    addFeedback: (state, action) => {
      state.feedback.push(action.payload);
    }
  }
});
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- AlertCard.test.tsx
```

## 📈 Performance Optimization

1. **Code Splitting**
   - Route-based splitting
   - Component lazy loading
   - Dynamic imports

2. **Caching**
   - API response caching
   - Local storage
   - Service workers

3. **Bundle Optimization**
   - Tree shaking
   - Minification
   - Compression

## 🔐 Security

- HTTPS enforcement
- XSS protection
- CSRF tokens
- Input sanitization

## 🐛 Troubleshooting

1. **Build Issues**
   - Clear node_modules
   - Update dependencies
   - Check TypeScript errors

2. **Runtime Issues**
   - Check console errors
   - Verify API connectivity
   - Test component isolation

3. **Performance Issues**
   - Profile with React DevTools
   - Check bundle size
   - Monitor API calls

## 📝 License

This project is licensed under the MIT License.
