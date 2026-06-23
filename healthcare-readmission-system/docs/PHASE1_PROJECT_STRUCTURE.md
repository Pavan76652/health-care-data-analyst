# Phase 1 — Project Structure

## Overview

`healthcare-readmission-system/` is a monorepo for the **Diabetes 130-US Hospitals** readmission prediction platform. It separates data science, backend APIs, frontend UI, analytics, and deployment so each layer can evolve independently while sharing a single source of truth.

```
healthcare-readmission-system/
├── backend/          # FastAPI application & ML inference
├── frontend/         # React + Bootstrap admin dashboard
├── database/         # PostgreSQL schema, SQL, migrations
├── notebooks/        # Jupyter EDA, cleaning, modeling experiments
├── dashboard/        # Power BI executive dashboard assets
├── models/           # Serialized ML models & SHAP artifacts
├── reports/          # Generated PDF/CSV business reports
├── data/             # Raw & processed datasets
├── deployment/       # Docker, Render, CI/CD configs
├── docs/             # Architecture, API, runbooks
└── tests/            # Unit & integration tests
```

---

## Folder Reference

### `backend/`

**Purpose:** Production FastAPI server that serves predictions, analytics, and patient data.

| Sub-area (planned) | Role |
|--------------------|------|
| `app/main.py` | Application entry point, CORS, routers |
| `app/api/` | REST routes: `/patients`, `/analytics`, `/dashboard`, `/predict` |
| `app/core/` | Config, security, database session |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response models |
| `app/services/` | Business logic, ML inference, SHAP explainability |
| `app/ml/` | Preprocessing pipeline loader, feature transforms |

**Why separate:** Keeps HTTP layer thin; ML and DB logic stay testable without spinning up the full web server.

---

### `frontend/`

**Purpose:** Hospital administrator-facing React SPA.

| Sub-area (planned) | Role |
|--------------------|------|
| `src/pages/` | Login, Dashboard, Patient Analytics, Prediction Tool, Reports |
| `src/components/` | Reusable charts (Chart.js), tables, filters |
| `src/services/` | API client calling FastAPI backend |
| `src/utils/` | CSV/PDF export helpers |

**Why separate:** UI releases can ship independently of model retraining; Bootstrap 5 ensures responsive layouts for tablets used on hospital floors.

---

### `database/`

**Purpose:** PostgreSQL as the system of record for patients, admissions, diagnoses, medications, and visits.

| Sub-area (planned) | Role |
|--------------------|------|
| `schema/` | `CREATE TABLE` scripts for all entities |
| `seeds/` | Sample `INSERT` scripts from cleaned dataset |
| `views/` | Analytics views (readmission rates, LOS aggregates) |
| `procedures/` | Stored procedures for KPI refresh |
| `indexes/` | Performance indexes on join/filter columns |
| `queries/` | 50+ healthcare analytics SQL queries |

**Why separate:** DBAs and analysts can run SQL without touching Python; Power BI connects directly here.

---

### `notebooks/`

**Purpose:** Reproducible research for data cleaning, EDA, and model development.

| Sub-area (planned) | Role |
|--------------------|------|
| `01_data_cleaning.ipynb` | Missing values, duplicates, encoding |
| `02_eda.ipynb` | Visualizations + business insights |
| `03_feature_engineering.ipynb` | Derived features for ML |
| `04_model_training.ipynb` | LR, RF, XGBoost comparison |
| `05_shap_explainability.ipynb` | SHAP plots for high-risk patients |

**Why separate:** Notebooks are exploratory; finalized logic moves into `backend/app/ml/` and `models/`.

---

### `dashboard/`

**Purpose:** Power BI executive dashboard for non-technical stakeholders.

| Sub-area (planned) | Role |
|--------------------|------|
| `readmission_executive.pbix` | Main dashboard file |
| `data_sources/` | Connection docs to PostgreSQL |
| `screenshots/` | README preview images |

**KPIs (planned):** Total patients, readmission rate, avg LOS, high-risk count, top diagnoses.

**Why separate:** Power BI artifacts don't belong in code repos mixed with Python; analysts own this folder.

---

### `models/`

**Purpose:** Versioned, serialized ML artifacts for production inference.

| Sub-area (planned) | Role |
|--------------------|------|
| `best_model.joblib` | Tuned XGBoost (or best performer) |
| `preprocessor.joblib` | Fitted sklearn `ColumnTransformer` |
| `feature_names.json` | Ordered feature list for API validation |
| `metrics.json` | ROC-AUC, F1, etc. from training run |
| `shap_explainer/` | Background data for SHAP values |

**Why separate:** Large binary files stay out of `backend/`; `.gitignore` excludes binaries while keeping the folder tracked.

---

### `reports/`

**Purpose:** Auto-generated and manual exports for compliance and leadership.

| Sub-area (planned) | Role |
|--------------------|------|
| `monthly_readmission_summary.pdf` | Scheduled executive summary |
| `high_risk_patients.csv` | Actionable discharge list |
| `templates/` | Report HTML/Jinja templates |

**Why separate:** Output artifacts are generated at runtime; templates live here for the Reports page and scheduled jobs.

---

### `data/`

**Purpose:** Dataset lifecycle from raw download to model-ready tables.

| Sub-area | Role |
|----------|------|
| `data/raw/` | Original Diabetes 130-US Hospitals CSV (from Kaggle) |
| `data/processed/` | Cleaned, encoded parquet/CSV after pipeline |
| `data/dictionaries/` | Column mappings, ICD code lookups |

**Why separate:** Clear boundary between immutable source data and derived artifacts; supports audit trails in healthcare.

---

### `deployment/`

**Purpose:** Containerization and cloud deployment to Render (or similar).

| Sub-area (planned) | Role |
|--------------------|------|
| `Dockerfile` | Multi-stage backend image |
| `docker-compose.yml` | Backend + PostgreSQL + optional frontend |
| `render.yaml` | Render Blueprint spec |
| `.env.example` | Required environment variables |

**Why separate:** DevOps concerns isolated from application code; one place for production topology.

---

### `docs/`

**Purpose:** Human-readable documentation for developers, analysts, and recruiters.

| Sub-area (planned) | Role |
|--------------------|------|
| `PHASE1_PROJECT_STRUCTURE.md` | This document |
| `API.md` | OpenAPI supplement, example requests |
| `DEPLOYMENT.md` | Step-by-step Render/Docker guide |
| `ARCHITECTURE.md` | System diagram, data flow |
| `RESUME_MATERIAL.md` | Phase 10 deliverables |

**Why separate:** Keeps the root README concise; deep dives live here.

---

### `tests/`

**Purpose:** Automated quality gates before deployment.

| Sub-area (planned) | Role |
|--------------------|------|
| `tests/backend/` | FastAPI endpoint tests, prediction schema |
| `tests/ml/` | Preprocessing pipeline, metric thresholds |
| `tests/database/` | Schema migration smoke tests |
| `conftest.py` | Shared fixtures (test DB, sample patient) |

**Why separate:** Mirrors `backend/` layout; pytest discovers tests without polluting production packages.

---

## Data Flow (High Level)

```
Kaggle CSV → data/raw/
     ↓
notebooks/ (clean + EDA) → data/processed/
     ↓
database/ (load PostgreSQL)
     ↓
notebooks/ (train) → models/
     ↓
backend/ (FastAPI + SHAP) ←→ frontend/ (React)
     ↓
dashboard/ (Power BI) ← database/
     ↓
reports/ (PDF/CSV exports)
```

---

## Target Deliverable Recap

| Component | Output |
|-----------|--------|
| ML target | Readmission within 30 days → **Risk Score 0–100** |
| Explainability | SHAP — why a patient is high risk |
| Users | Hospital administrators with actionable recommendations |

---

## Next Phase

**Phase 2 — Data Cleaning:** Download dataset, run missing-value analysis, build preprocessing pipeline.

*Awaiting your approval before proceeding.*
