# Phase 7 — FastAPI Backend (Complete)

## Overview

FastAPI backend is implemented with production-friendly structure and endpoints for patient listing, analytics, dashboard payloads, and model inference.

Base URL:

`http://localhost:8000/api/v1`

Swagger UI:

`http://localhost:8000/docs`

## Endpoints

### `GET /health`
Simple service health check.

### `GET /patients`
Paginated patient/admission records.

Query params:
- `page` (default `1`)
- `page_size` (default `25`, max `200`)
- `search` (optional text for patient id, gender, diagnosis group)

### `GET /analytics`
Returns KPIs and analytics aggregates:
- Total patients
- Total admissions
- 30-day readmission rate
- Average length of stay
- High-risk patient count
- Readmission by age
- Top diagnoses

### `GET /dashboard`
Returns Power BI-ready dashboard payload:
- KPI summary
- Readmission by age/gender/diagnosis
- Monthly trends
- Medication analysis

### `POST /predict`
Predicts readmission probability and risk score.

Required input:
- `age`
- `gender`
- `diagnosis`
- `time_in_hospital`
- `number_of_medications`
- `number_of_procedures`

Response:
- `readmission_probability`
- `risk_score` (0–100)
- `risk_level` (`Low` / `Moderate` / `High`)
- `recommendation`
- `top_risk_factors`

## Example Prediction Request

```json
{
  "age": 68,
  "gender": "Female",
  "diagnosis": "Circulatory_390_459",
  "time_in_hospital": 6,
  "number_of_medications": 18,
  "number_of_procedures": 2
}
```

## Run API

```bash
pip install -r requirements.txt
python backend/scripts/run_api.py
```

## Project Files Added

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/core/config.py`
- `backend/app/schemas/predict.py`
- `backend/app/services/data_service.py`
- `backend/app/services/prediction_service.py`
- `backend/scripts/run_api.py`

## Notes

- API uses generated analytics datasets from `dashboard/data`.
- Prediction endpoint loads `models/best_model.joblib`.
- If model file is missing, `/predict` returns `503`.

## Next Phase

Phase 8 — React Frontend integration with this API.
