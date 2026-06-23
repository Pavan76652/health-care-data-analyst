# Healthcare Readmission — Power BI Executive Dashboard

## Quick Start (15 minutes)

### Step 1 — Generate data
```bash
python dashboard/scripts/generate_powerbi_data.py
```

### Step 2 — Open Power BI Desktop
Download: https://powerbi.microsoft.com/desktop/

### Step 3 — Import data
1. **Get Data** → **Text/CSV**
2. Select `dashboard/data/fact_admissions.csv`
3. Click **Transform Data** → verify column types → **Close & Apply**

### Step 4 — Import theme (optional)
**View** → **Themes** → **Browse for themes** → `dashboard/themes/executive_theme.json`

### Step 5 — Add DAX measures
**Modeling** → **New Measure** → copy from `dashboard/dax/kpi_measures.dax`

### Step 6 — Build visuals (see layout below)

---

## Dashboard Layout — Page 1: Executive Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEALTHCARE READMISSION ANALYTICS          [Filter: Year] [Risk Tier]  │
├──────────┬──────────┬──────────┬──────────┬──────────┬────────────────┤
│  Total   │ Readmit  │  Avg LOS │  High    │   Top    │                │
│ Patients │  Rate %  │  (days)  │  Risk    │ Diagnosis│                │
│  71,518  │  11.16%  │   4.4    │  12,450  │ Circulat.│                │
├──────────┴──────────┴──────────┴──────────┴──────────┴────────────────┤
│  Readmission by Age (Bar)    │  Readmission by Gender (Donut)          │
├──────────────────────────────┼────────────────────────────────────────┤
│  Monthly Trends (Line)       │  Top Diagnoses (Horizontal Bar)        │
├──────────────────────────────┴────────────────────────────────────────┤
│  Medication Analysis (Clustered Bar)  │  Risk Tier Breakdown (Treemap) │
└───────────────────────────────────────────────────────────────────────┘
```

## KPI Definitions

| KPI | Source | DAX Measure |
|-----|--------|-------------|
| Total Patients | `fact_admissions` | `[Total Patients]` |
| Readmission Rate | 30-day readmit % | `[Readmission Rate %]` |
| Average LOS | Days in hospital | `[Average Length of Stay]` |
| High Risk Patients | Risk tier High/Critical | `[High Risk Patients]` |
| Top Diagnoses | Primary ICD group | `diag_1_group` on bar chart |

## Chart Specifications

| Chart | Type | Fields |
|-------|------|--------|
| Readmission by Age | Clustered bar | Axis: `age`, Values: `readmission_rate_pct` or measure |
| Readmission by Gender | Donut | Legend: `gender`, Values: admissions |
| Readmission by Diagnosis | Horizontal bar | Axis: `diag_1_group`, Values: count |
| Monthly Trends | Line chart | Axis: `month_name`, Values: admissions + readmission rate |
| Medication Analysis | Bar chart | Import `medication_analysis.csv`, Axis: `medication_name` |
| Risk Tier | Treemap | Group: `risk_tier`, Values: count |

## Data Files

| File | Rows | Use |
|------|------|-----|
| `fact_admissions.csv` | 101,766 | Primary fact table |
| `kpi_summary.csv` | 1 | Pre-built KPI card values |
| `readmission_by_age.csv` | 10 | Age chart (optional direct import) |
| `readmission_by_gender.csv` | 2 | Gender chart |
| `readmission_by_diagnosis.csv` | 15 | Diagnosis chart |
| `monthly_trends.csv` | ~120 | Trend line chart |
| `medication_analysis.csv` | 23 | Medication chart |
| `high_risk_patients.csv` | 5,000 | Drill-through detail table |
| `executive_dashboard_master.csv` | 101,766 | Single-file quick import |

## PostgreSQL Connection (Alternative)

If database is loaded (Phase 3):

```
Get Data → PostgreSQL database
Server: localhost
Database: healthcare_readmission
Tables: healthcare.admissions, healthcare.patients, healthcare.diagnosis
Views: healthcare.v_readmission_summary, healthcare.v_high_risk_patients
```

## Filters (Slicers)

Add slicers for:
- `gender`
- `age`
- `risk_tier`
- `admission_year`
- `diag_1_group`

## Publish

1. **Publish** → Power BI Service
2. Set scheduled refresh for CSV folder or PostgreSQL
3. Share with hospital administrator security group

## Files in This Folder

```
dashboard/
├── data/                  # CSV datasets (generated)
├── dax/                   # DAX measure definitions
├── power_query/           # M scripts for data load
├── themes/                # Executive color theme
├── scripts/               # Data generation script
└── README.md              # This file
```
