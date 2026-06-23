# Phase 3 — SQL Database (Complete)

## Schema Overview

```
healthcare (schema)
├── ref_admission_type          Lookup
├── ref_discharge_disposition   Lookup
├── ref_admission_source        Lookup
├── patients                    71,518 rows
├── admissions                  101,766 rows
├── diagnosis                   303,496 rows
├── medications                 2,340,618 rows
└── hospital_visits             305,298 rows
```

## Entity Relationship

```mermaid
erDiagram
    patients ||--o{ admissions : has
    patients ||--o{ diagnosis : has
    patients ||--o{ medications : receives
    patients ||--o{ hospital_visits : prior
    admissions ||--o{ diagnosis : includes
    admissions ||--o{ medications : includes
    admissions ||--o{ hospital_visits : includes
    ref_admission_type ||--o{ admissions : classifies
    ref_discharge_disposition ||--o{ admissions : classifies
    ref_admission_source ||--o{ admissions : classifies
```

## Tables

| Table | Purpose |
|-------|---------|
| `patients` | Demographics — race, gender, age bracket |
| `admissions` | Encounter-level facts — LOS, readmission, meds count |
| `diagnosis` | ICD-9 codes (ranks 1–3) per admission |
| `medications` | 23 diabetes drugs with dosage status per admission |
| `hospital_visits` | Prior-year outpatient, ER, inpatient counts |

## Files

| Path | Description |
|------|-------------|
| `schema/01_create_tables.sql` | CREATE TABLE scripts |
| `seeds/01_reference_inserts.sql` | Lookup table INSERTs |
| `seeds/02_sample_inserts.sql` | Sample INSERT (5 rows each) |
| `seeds/03_bulk_load.sql` | PostgreSQL `\copy` bulk load |
| `seeds/csv/*.csv` | Normalized seed data |
| `indexes/create_indexes.sql` | 16 performance indexes |
| `views/analytics_views.sql` | 7 analytics views |
| `procedures/stored_procedures.sql` | 7 functions + 2 procedures |
| `queries/healthcare_analytics_50_queries.sql` | **50 analytics queries** |
| `init_database.sql` | Master setup script |
| `scripts/generate_seed_data.py` | CSV generator from cleaned data |
| `scripts/load_to_postgres.py` | Python bulk loader |

## Setup Instructions

### 1. Create database

```sql
CREATE DATABASE healthcare_readmission;
```

### 2. Initialize schema

```bash
psql -U postgres -d healthcare_readmission -f database/init_database.sql
```

### 3. Generate seed CSVs

```bash
python database/scripts/generate_seed_data.py
```

### 4. Load data

**Option A — psql COPY:**
```bash
psql -U postgres -d healthcare_readmission -f database/seeds/03_bulk_load.sql
```

**Option B — Python:**
```bash
set DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/healthcare_readmission
pip install sqlalchemy psycopg2-binary
python database/scripts/load_to_postgres.py
```

### 5. Verify

```sql
SELECT * FROM healthcare.fn_dashboard_kpis();
SELECT * FROM healthcare.v_readmission_summary;
```

## Views

| View | Purpose |
|------|---------|
| `v_readmission_summary` | Executive KPIs |
| `v_readmission_by_demographics` | Gender/age/race breakdown |
| `v_readmission_by_diagnosis` | ICD group readmission rates |
| `v_medication_analysis` | Drug-level analysis |
| `v_patient_admission_detail` | Full encounter for API |
| `v_high_risk_patients` | Actionable risk tiers |
| `v_utilization_summary` | Prior visit aggregates |

## Stored Procedures / Functions

| Name | Returns |
|------|---------|
| `fn_dashboard_kpis()` | KPI row set |
| `fn_readmission_rate_by_gender()` | Gender breakdown |
| `fn_readmission_rate_by_age()` | Age bracket breakdown |
| `fn_top_diagnoses_by_readmission(limit)` | Top ICD groups |
| `fn_patient_readmission_history(patient_id)` | Patient timeline |
| `fn_insulin_readmission_rate()` | Insulin vs readmission |
| `sp_log_etl_refresh(source, rows)` | ETL logging |

## Sample Analytics Queries (from 50)

- **Q1** — Most readmitted age groups
- **Q2** — Readmission rate by gender
- **Q11** — Average length of stay
- **Q19** — Diagnosis causing maximum readmission
- **Q27** — Medication analysis by drug
- **Q50** — Executive summary (all KPIs)

Full list: `database/queries/healthcare_analytics_50_queries.sql`

## Next Phase

**Phase 4 — EDA:** Visualizations and business insights.

*Awaiting approval to proceed.*
