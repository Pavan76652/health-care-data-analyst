# Phase 9 — Deployment (Complete)

## Overview

Production deployment assets for Docker (local/cloud) and Render (hosted).

| Asset | Path |
|-------|------|
| Backend Dockerfile | `backend/Dockerfile` |
| Frontend Dockerfile | `frontend/Dockerfile` |
| Docker Compose | `deployment/docker-compose.yml` |
| Environment template | `deployment/.env.example` |
| Render Blueprint | `deployment/render.yaml` |
| API requirements (prod) | `backend/requirements.txt` |

---

## Architecture (Docker)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend    │────▶│ PostgreSQL  │
│  nginx :80  │ /api│  FastAPI     │     │   :5432     │
│  React SPA  │     │  :8000       │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
```

- **Frontend** serves the React build and proxies `/api` to the backend.
- **Backend** loads ML model from `models/best_model.joblib` and dashboard CSVs.
- **PostgreSQL** initializes schema on first run (optional for API; CSV mode works without DB).

---

## Option A — Docker Compose (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Model trained: `models/best_model.joblib` exists
- Dashboard data generated: `python dashboard/scripts/generate_powerbi_data.py`

### Steps

```bash
cd deployment
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD

docker compose up --build -d
```

### Access

| Service | URL |
|---------|-----|
| **React UI** | http://localhost |
| **FastAPI** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 |

### Login
- Email: `admin@hospital.com`
- Password: `admin123`

### Useful commands

```bash
docker compose ps
docker compose logs -f backend
docker compose down
docker compose down -v   # remove volumes
```

---

## Option B — Local Development (No Docker)

**Terminal 1 — API:**
```bash
pip install -r backend/requirements.txt
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — UI:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Option C — Render (Cloud)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Healthcare readmission system"
git remote add origin https://github.com/YOUR_USERNAME/healthcare-readmission-system.git
git push -u origin main
```

### 2. Deploy via Blueprint

1. Go to [render.com](https://render.com) → **New** → **Blueprint**
2. Connect your GitHub repo
3. Render reads `deployment/render.yaml`
4. Set environment secrets in dashboard:
   - `POSTGRES_PASSWORD`
   - Update `VITE_API_URL` to your API service URL after first deploy

### 3. Services created

| Service | Type |
|---------|------|
| `healthcare-readmission-api` | Python web (FastAPI) |
| `healthcare-readmission-ui` | Static site (React) |
| `healthcare-readmission-db` | PostgreSQL |

### Note on Render free tier
- API may spin down after inactivity (cold start ~30s)
- Upload `models/best_model.joblib` via build or include in repo (git-lfs if large)
- Ensure `dashboard/data/*.csv` is committed or generated in build step

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | DB username | `postgres` |
| `POSTGRES_PASSWORD` | DB password | *(required)* |
| `POSTGRES_DB` | Database name | `healthcare_readmission` |
| `DATABASE_URL` | SQLAlchemy connection string | auto in compose |
| `CORS_ORIGINS` | Allowed frontend origins (JSON) | `["*"]` |
| `DEBUG` | FastAPI debug mode | `false` |
| `VITE_API_URL` | Frontend API base URL | `/api/v1` |

Copy `deployment/.env.example` → `deployment/.env` before running Docker.

---

## Pre-deploy Checklist

- [ ] `models/best_model.joblib` exists (run `python backend/scripts/run_training.py`)
- [ ] `dashboard/data/fact_admissions.csv` exists (run `python dashboard/scripts/generate_powerbi_data.py`)
- [ ] `data/processed/cleaned_data.csv` exists (run `python backend/scripts/run_cleaning.py`)
- [ ] `.env` configured with strong password
- [ ] Docker images build: `docker compose build`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `/predict` returns 503 | Train model: `python backend/scripts/run_training.py` |
| Dashboard empty | Generate data: `python dashboard/scripts/generate_powerbi_data.py` |
| Frontend can't reach API | Check nginx proxy; use `/api/v1` not full URL in Docker |
| CORS errors | Set `CORS_ORIGINS` to your frontend URL |
| Postgres connection failed | Wait for `db` healthcheck; verify `DATABASE_URL` |

---

## Next Phase

**Phase 10 — Resume Material:** GitHub README polish, resume description, STAR interview, business impact analysis.

*Awaiting approval to proceed.*
