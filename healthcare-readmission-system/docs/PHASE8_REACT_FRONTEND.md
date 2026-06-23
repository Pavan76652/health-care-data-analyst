# Phase 8 — React Frontend (Complete)

## Overview

Responsive React SPA for hospital administrators with Bootstrap 5 UI, Chart.js visualizations, and full FastAPI integration.

## Pages Built

### 1. Login (`/login`)
- Demo authentication (`admin@hospital.com` / `admin123`)
- Session stored in `localStorage`

### 2. Dashboard (`/dashboard`)
- KPI cards: patients, readmission rate, LOS, high risk, top diagnosis
- Charts: age, gender, monthly trends, diagnoses
- Data source: `GET /api/v1/dashboard`

### 3. Patient Analytics (`/patients`)
- Paginated patient table
- Search by patient ID, gender, diagnosis
- Risk tier filter
- **Export CSV**

### 4. Prediction Tool (`/predict`)
- Form: age, gender, diagnosis, LOS, medications, procedures
- Calls `POST /api/v1/predict`
- Shows risk score (0–100), risk level, recommendation, risk factors

### 5. Reports (`/reports`)
- Executive KPI summary
- Diagnosis readmission chart
- Age breakdown table
- **Export CSV** and **Export PDF**

## Run Instructions

```bash
# Terminal 1
python backend/scripts/run_api.py

# Terminal 2
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Project Structure

```
frontend/
├── src/
│   ├── api/client.js
│   ├── components/Layout.jsx, KpiCard.jsx
│   ├── context/AuthContext.jsx
│   ├── pages/Login, Dashboard, PatientAnalytics, PredictionTool, Reports
│   └── utils/exportCsv.js, exportPdf.js
├── package.json
└── vite.config.js
```

## Features Checklist

- [x] Login
- [x] Dashboard
- [x] Patient Analytics
- [x] Prediction Tool
- [x] Reports
- [x] Filters & search
- [x] Chart.js charts
- [x] Export CSV
- [x] Export PDF
- [x] Responsive Bootstrap UI

## Next Phase

**Phase 9 — Deployment:** Docker, docker-compose, Render guide.

*Awaiting approval to proceed.*
