# Healthcare Patient Readmission Prediction System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange.svg)](https://xgboost.readthedocs.io)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://postgresql.org)

> **Predict 30-day hospital readmission risk** using machine learning on 101,766 real diabetic patient admissions — with executive dashboards, REST API, and admin portal for hospital administrators.

![Dashboard](docs/assets/dashboard-preview.png)

---

## Problem

Hospitals lose **$15,000+ per readmission** and face **Medicare penalties** when patients return within 30 days. This system identifies at-risk patients **before discharge** using historical clinical data.

## Solution

| Layer | Technology | Deliverable |
|-------|------------|-------------|
| Data | Pandas, sklearn pipeline | Cleaned 101K records, 84 ML features |
| Database | PostgreSQL | 5 tables, 50 SQL queries, views & procedures |
| Analytics | EDA, Power BI | 7 visualizations, executive KPI dashboard |
| ML | XGBoost | **ROC-AUC 0.69**, risk score 0–100 |
| API | FastAPI | `/predict`, `/patients`, `/analytics`, `/dashboard` |
| UI | React + Bootstrap 5 | Admin portal with charts, search, CSV/PDF export |
| DevOps | Docker, Render | One-command deployment |

---

## Key Results

| Metric | Value |
|--------|-------|
| Dataset size | **101,766** admissions, **71,518** patients |
| 30-day readmission rate | **11.16%** |
| Best model | **XGBoost** (ROC-AUC **0.6866**) |
| High-risk patients flagged | **58,550** |
| Top predictor | Prior inpatient visits |

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/healthcare-readmission-system.git
cd healthcare-readmission-system
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2. Run locally
```bash
# Terminal 1 — API
cd backend && python -m uvicorn app.main:app --port 8000

# Terminal 2 — UI
cd frontend && npm run dev
```

Open **http://localhost:5173** — Login: `admin@hospital.com` / `admin123`

### 3. Docker (full stack)
```bash
cd deployment && cp .env.example .env && docker compose up --build -d
```

Open **http://localhost**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/patients` | Paginated patient list + search |
| `GET` | `/api/v1/analytics` | KPIs and aggregates |
| `GET` | `/api/v1/dashboard` | Dashboard chart data |
| `POST` | `/api/v1/predict` | ML readmission risk prediction |

**Swagger docs:** http://localhost:8000/docs

---

## Project Structure

```
healthcare-readmission-system/
├── backend/          # FastAPI + ML inference
├── frontend/         # React admin portal
├── database/         # PostgreSQL schema, 50 SQL queries
├── notebooks/        # Jupyter EDA & ML notebooks
├── dashboard/        # Power BI datasets & DAX
├── models/           # Trained XGBoost model
├── deployment/       # Docker Compose, Render blueprint
└── docs/             # Phase documentation
```

---

## Dataset

**Diabetes 130-US Hospitals for years 1999-2008**  
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)

```bash
curl -L -o data/raw/diabetes-130-us-hospitals.zip \
  "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
```

---

## Documentation

| Phase | Document |
|-------|----------|
| Architecture | [PHASE1_PROJECT_STRUCTURE.md](docs/PHASE1_PROJECT_STRUCTURE.md) |
| Data Cleaning | [PHASE2_DATA_CLEANING.md](docs/PHASE2_DATA_CLEANING.md) |
| SQL Database | [PHASE3_SQL_DATABASE.md](docs/PHASE3_SQL_DATABASE.md) |
| EDA | [PHASE4_EDA.md](docs/PHASE4_EDA.md) |
| Machine Learning | [PHASE5_MACHINE_LEARNING.md](docs/PHASE5_MACHINE_LEARNING.md) |
| Power BI | [PHASE6_POWER_BI.md](docs/PHASE6_POWER_BI.md) |
| FastAPI | [PHASE7_FASTAPI_BACKEND.md](docs/PHASE7_FASTAPI_BACKEND.md) |
| React UI | [PHASE8_REACT_FRONTEND.md](docs/PHASE8_REACT_FRONTEND.md) |
| Deployment | [PHASE9_DEPLOYMENT.md](docs/PHASE9_DEPLOYMENT.md) |
| **Resume / Interview** | [RESUME_MATERIAL.md](docs/RESUME_MATERIAL.md) |

---

## Resume & Portfolio

See **[docs/RESUME_MATERIAL.md](docs/RESUME_MATERIAL.md)** for:
- Resume bullet points
- Recruiter pitch (30 seconds)
- STAR interview answers
- Healthcare business impact analysis ($8.8M savings estimate)
- ATS keyword skills list

---

## Author

**Arjun Goud** — Healthcare Data Analyst | Data Scientist | Full Stack Developer

---

## License

MIT License — Educational / portfolio project. Dataset © UCI ML Repository.
