# Phase 6 — Power BI Executive Dashboard (Complete)

## Overview

Executive-level **Hospital Administrator Dashboard** for readmission analytics, built with Power BI Desktop using pre-aggregated datasets and DAX measures.

> **Note:** `.pbix` files are binary Power BI Desktop projects. This phase delivers all **data, DAX, themes, Power Query, and step-by-step build instructions** so you can create the dashboard in ~15 minutes.

---

## KPIs (Live Values from Dataset)

| KPI | Value |
|-----|-------|
| **Total Patients** | 71,518 |
| **Total Admissions** | 101,766 |
| **Readmission Rate (30-day)** | 11.16% |
| **Average Length of Stay** | 4.4 days |
| **High Risk Patients** | 58,550 |
| **Top Diagnosis** | Circulatory_390_459 |

---

## Dashboard Pages

### Page 1 — Executive Summary
- 5 KPI cards across the top
- Readmission by Age (bar chart)
- Readmission by Gender (donut)
- Monthly admission trends (line)
- Top diagnoses by volume (horizontal bar)
- Medication analysis (bar)
- Risk tier treemap

### Page 2 — High Risk Patients (Drill-through)
- Table: `high_risk_patients.csv` (top 5,000)
- Columns: patient ID, gender, age, risk tier, medications, prior visits, diagnosis
- **Actionable:** Export list for care management team follow-up

---

## Charts Delivered (Data Ready)

| Chart | Data File | Insight |
|-------|-----------|---------|
| Readmission by Age | `readmission_by_age.csv` | `[70-80)` highest volume; `[20-30)` highest rate |
| Readmission by Gender | `readmission_by_gender.csv` | Female 53.8%; rates nearly equal |
| Readmission by Diagnosis | `readmission_by_diagnosis.csv` | Circulatory disease dominates volume |
| Monthly Trends | `monthly_trends.csv` | Seasonal admission patterns 1999–2008 |
| Medication Analysis | `medication_analysis.csv` | Insulin most prescribed; 12% readmit rate |
| Risk Breakdown | `fact_admissions.risk_tier` | Critical/High/Moderate/Low tiers |

---

## Business Insights for Administrators

### 1. Revenue Risk
At **11.16%** 30-day readmission, this hospital cohort exceeds CMS benchmarks. Each avoided readmission saves **$10,000–$15,000** in penalties and care costs.

### 2. Target Population
**67%** of patients are 60+. Allocate transitional care nurses to the geriatric diabetes unit.

### 3. Diagnosis Focus
**Circulatory complications** (ICD 390–459) are the #1 primary diagnosis. Implement CHF + diabetes co-management protocols.

### 4. Medication Complexity
Patients on **insulin** readmit at **12.1%** vs **10.0%** without. Mandate pharmacist discharge counseling for insulin patients.

### 5. High-Risk Cohort
Patients with **3+ prior visits** or **15+ medications** are flagged High/Critical. Use `high_risk_patients.csv` for weekly care management rounds.

---

## Build Instructions

### Generate Data
```bash
python dashboard/scripts/generate_powerbi_data.py
```

### Power BI Desktop
1. Import `dashboard/data/fact_admissions.csv`
2. Apply theme: `dashboard/themes/executive_theme.json`
3. Paste DAX from `dashboard/dax/kpi_measures.dax`
4. Build visuals per `dashboard/README.md` layout

### PostgreSQL (Optional)
Connect to `healthcare.v_readmission_summary` and related views from Phase 3.

---

## Deliverables

| Asset | Path |
|-------|------|
| Fact table CSV | `dashboard/data/fact_admissions.csv` |
| KPI summary | `dashboard/data/kpi_summary.csv` |
| Chart datasets | `dashboard/data/readmission_*.csv` |
| DAX measures | `dashboard/dax/kpi_measures.dax` |
| Power Query M | `dashboard/power_query/load_fact_admissions.m` |
| Executive theme | `dashboard/themes/executive_theme.json` |
| Setup guide | `dashboard/README.md` |

---

## Next Phase

**Phase 7 — FastAPI Backend:** REST APIs (`/patients`, `/analytics`, `/dashboard`, `/predict`) with ML inference.

*Awaiting approval to proceed.*
