# Phase 2 — Data Cleaning (Complete)

## Summary

| Metric | Value |
|--------|-------|
| Raw records | 101,766 |
| Cleaned records | 101,766 |
| Duplicates removed | 0 |
| ML feature matrix | 101,766 × 84 |
| 30-day readmission rate | 11.16% |
| Data quality grade | B (see report) |

## Pipeline Steps

### 1. Missing Value Analysis
- Normalized `?`, `None`, `NULL` → NaN
- **Dropped** (>40% missing): `weight`, `max_glu_serum`, `A1Cresult`, `payer_code`, `medical_specialty`
- **Imputed** remaining categoricals with `Unknown`; numerics with median (in sklearn pipeline)

### 2. Duplicate Removal
- Exact duplicate rows: **0**
- Duplicate clinical records (excluding IDs): **0**
- 71,518 unique patients; 30,248 repeat admissions retained (valid)

### 3. Data Quality Assessment
- Report: `reports/data_quality_report.json`
- Completeness impacted mainly by sparse lab columns (now dropped)

### 4. Outlier Analysis
- IQR method on utilization and clinical numerics
- **16.45%** outlier rate on `number_outpatient` (right-skewed; mostly zeros)
- Outliers **flagged** via `high_utilization_flag`, not removed

### 5. Feature Engineering
| Feature | Description |
|---------|-------------|
| `age_midpoint` | Numeric age from bracket (e.g. `[60-70)` → 65) |
| `total_prior_visits` | Outpatient + emergency + inpatient (prior year) |
| `active_medication_count` | Count of meds with Steady/Up/Down |
| `on_insulin` | Binary insulin usage |
| `had_prior_inpatient` | Prior inpatient visit flag |
| `had_prior_emergency` | Prior ER visit flag |
| `diag_*_group` | ICD-9 category (Diabetes, Circulatory, etc.) |
| `readmitted_30_days` | **Target**: 1 if `<30`, else 0 |
| `high_utilization_flag` | IQR outlier on prior visits |

### 6. Encoding
- `ColumnTransformer`: StandardScaler + OneHotEncoder
- Saved as `models/preprocessor.joblib`

## Outputs

| File | Purpose |
|------|---------|
| `data/processed/cleaned_data.csv` | Cleaned + engineered dataset |
| `models/preprocessor.joblib` | Fitted sklearn pipeline |
| `reports/data_quality_report.json` | Full quality metrics |
| `reports/phase2_cleaning_summary.json` | Run summary |
| `data/dictionaries/column_definitions.json` | Column metadata |
| `notebooks/01_data_cleaning.ipynb` | Interactive walkthrough |

## Run Pipeline

```bash
pip install -r requirements.txt
python backend/scripts/run_cleaning.py
```

## Key Business Insights

1. **Class imbalance** — Only 11% readmitted within 30 days; models need balanced metrics (recall, F1, ROC-AUC).
2. **High-missing labs** — HbA1c and glucose labs are 83–95% missing; cannot rely on them for prediction.
3. **Prior utilization matters** — Outpatient/ER/inpatient history is highly skewed; strong readmission signal expected.
4. **Repeat patients** — 30% of rows are return admissions; patient-level grouping may help in advanced modeling.

## Next Phase

**Phase 3 — SQL Database:** PostgreSQL schema, inserts, views, stored procedures, 50 analytics queries.

*Awaiting approval to proceed.*
