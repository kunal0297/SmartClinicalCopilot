# Frontend - Clinical Rules Application

## Overview

This React + TypeScript frontend uses Material UI and Axios to connect to the FastAPI backend for clinical rules, FHIR patient data, and LLM explanations.

## Available Scripts

- **`npm run dev`**  
  Starts the app in development mode.  
  Open [http://localhost:3000](http://localhost:3000) in your browser.

- **`npm run build`**  
  Builds the app for production into the `dist` folder.

- **`npm run preview`**  
  Serves the built app locally for preview.

## Project Structure

- `src/components/` — React components (AlertCard, PatientViewer, RuleEditor)
- `src/pages/` — Page-level component (Dashboard)
- `src/api.ts` — API client connecting to backend services
- `src/App.tsx` — Root component with routing
- `src/index.tsx` — React app entry point

## Setup

1. Install dependencies:

   ```bash
   npm install
Run the app in dev mode:


npm run dev
The frontend expects backend API at http://localhost:8000/. Modify api.ts if needed.

Features
Displays patient information fetched from backend FHIR service.
Lists clinical alerts triggered by rule matches.
Allows entering custom rule texts to search.
Click alert to get LLM-generated explanation.
Technologies
React 18 + TypeScript
Material UI (MUI)
Axios for HTTP requests
React Router v6
Vite build system
Notes
Make sure backend server is running at the configured URL.
Extend components or add authentication as per your requirements.

undefined
