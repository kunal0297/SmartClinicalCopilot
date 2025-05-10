# Smart Clinical Copilot Frontend 🎨

[![Powered by InterSystems IRIS for Health](https://img.shields.io/badge/Powered%20by-IRIS%20for%20Health-blue)](https://www.intersystems.com/iris/)

A modern, responsive frontend for the Smart Clinical Copilot system, built with React, TypeScript, shadcn/ui, and Tailwind CSS.

## ✨ Features

- **Live IRIS FHIR integration** (search real patient IDs)
- **Cohort Analytics**: Real-time charts and summary cards from IRIS Health
- **FHIR Resource Explorer**: Browse any FHIR resource type
- **Dark/Light Mode**: Global toggle, animated transitions
- **Modern, responsive UI**: MUI, custom cards, glowing hero effects, animated text
- **Animated Hero Prompt**: TextGenerateEffect with framer-motion and Tailwind
- **Patient Management**: Search, view, and analyze real patient data
- **Rule Matching & Explainability**: Alerts, LLM/SHAP explanations

## 🏥 IRIS for Health Integration
- Requires a running IRIS for Health FHIR server (see backend README)
- Enter a real patient ID from IRIS to view data and analytics

## 🧑‍💻 Demo/Test Patient IDs
- Use a real patient ID from your IRIS FHIR instance. For demo, try: `1`, `2`, or use the FHIR Patient browser in IRIS to find IDs.
- If you have no data, use the FHIR "Try It" feature in IRIS to create a patient.

## 🖼️ Screenshots
<!-- Add screenshots here for contest submission -->

## 🛠️ Technical Stack

- **Framework**: React 19
- **Language**: TypeScript
- **Styling**: Material-UI, Tailwind CSS v4, shadcn/ui
- **State Management**: Redux Toolkit
- **API Client**: Axios
- **Animation**: framer-motion
- **Build Tool**: Vite

## 📦 Dependencies

```json
{
  "dependencies": {
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.0",
    "@mui/icons-material": "^7.1.0",
    "@mui/material": "^7.1.0",
    "@types/recharts": "^1.8.29",
    "axios": "^1.9.0",
    "framer-motion": "^12.10.5",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-router-dom": "^7.5.3",
    "recharts": "^2.15.3",
    "simplex-noise": "^4.0.3"
  },
  "devDependencies": {
    "@eslint/js": "^9.25.0",
    "@types/react": "^19.1.2",
    "@types/react-dom": "^19.1.2",
    "@vitejs/plugin-react": "^4.4.1",
    "eslint": "^9.25.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.19",
    "globals": "^16.0.0",
    "typescript": "~5.8.3",
    "typescript-eslint": "^8.30.1",
    "vite": "^6.3.5"
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

## ✨ Animated Hero Prompt

The homepage features an animated hero prompt using the `TextGenerateEffect` component, powered by framer-motion and styled with Tailwind CSS. You can find the component in `src/components/ui/text-generate-effect.tsx` and the demo in `src/components/text-generate-effect-demo.tsx`.

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

### 5. Animated Hero Prompt (TextGenerateEffect)
```tsx
<TextGenerateEffect />
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
   - Smooth and animated transitions (framer-motion)
   - Animated hero prompt and glowing effects
   - Error handling
   - Loading states

5. **Visual Polish**
   - Animated text hero
   - Glowing/gradient hover effects
   - Vortex animated background (dark mode)
   - Modern cards with blur and glassmorphism

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
