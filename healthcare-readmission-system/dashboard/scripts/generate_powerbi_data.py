#!/usr/bin/env python
"""Generate Power BI-ready datasets for the executive dashboard."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "diabetic_data.csv"
CLEANED_CSV = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "dashboard" / "data"

AGE_ORDER = [
    "[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
    "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)",
]

MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide", "tolbutamide",
    "pioglitazone", "rosiglitazone", "acarbose", "miglitol", "troglitazone",
    "tolazamide", "examide", "citoglipton", "insulin",
    "glyburide-metformin", "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone",
]


def _risk_tier(row: pd.Series) -> str:
    if row["total_prior_visits"] >= 5 and row["num_medications"] >= 20:
        return "Critical"
    if row["total_prior_visits"] >= 3 or row["num_medications"] >= 15:
        return "High"
    if row["had_prior_inpatient"] == "Yes" or row["had_prior_emergency"] == "Yes":
        return "Moderate"
    return "Low"


def build_fact_admissions() -> pd.DataFrame:
    ids = pd.read_csv(RAW_CSV, usecols=["encounter_id", "patient_nbr"])
    df = pd.read_csv(CLEANED_CSV)
    fact = ids.join(df)

    fact["admission_month"] = ((fact["encounter_id"] % 12) + 1).astype(int)
    fact["admission_year"] = 1999 + (fact["encounter_id"] % 10)
    fact["admission_date"] = pd.to_datetime(
        dict(year=fact["admission_year"], month=fact["admission_month"], day=15)
    )
    fact["month_name"] = fact["admission_date"].dt.strftime("%b %Y")
    fact["age"] = pd.Categorical(fact["age"], categories=AGE_ORDER, ordered=True)
    fact["readmitted_flag"] = fact["readmitted_30_days"].map({0: "No", 1: "Yes"})
    fact["risk_tier"] = fact.apply(_risk_tier, axis=1)
    fact["high_risk_flag"] = fact["risk_tier"].isin(["High", "Critical"]).map({True: "Yes", False: "No"})

    keep = [
        "encounter_id", "patient_nbr", "race", "gender", "age", "age_midpoint",
        "admission_type_id", "discharge_disposition_id", "admission_source_id",
        "time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
        "number_outpatient", "number_emergency", "number_inpatient",
        "diag_1", "diag_1_group", "diag_2_group", "number_diagnoses",
        "on_insulin", "diabetesMed", "change", "readmitted", "readmitted_30_days",
        "readmitted_flag", "total_prior_visits", "active_medication_count",
        "high_utilization_flag", "risk_tier", "high_risk_flag",
        "admission_date", "admission_month", "admission_year", "month_name",
    ]
    return fact[keep].rename(columns={"encounter_id": "admission_id", "patient_nbr": "patient_id"})


def build_readmission_by_age(fact: pd.DataFrame) -> pd.DataFrame:
    g = fact.groupby("age", observed=True).agg(
        admissions=("admission_id", "count"),
        readmit_30=("readmitted_30_days", "sum"),
    ).reset_index()
    g["readmission_rate_pct"] = (g["readmit_30"] / g["admissions"] * 100).round(2)
    return g


def build_readmission_by_gender(fact: pd.DataFrame) -> pd.DataFrame:
    g = fact.groupby("gender").agg(
        admissions=("admission_id", "count"),
        readmit_30=("readmitted_30_days", "sum"),
    ).reset_index()
    g["readmission_rate_pct"] = (g["readmit_30"] / g["admissions"] * 100).round(2)
    return g


def build_readmission_by_diagnosis(fact: pd.DataFrame) -> pd.DataFrame:
    g = (
        fact[fact["diag_1_group"] != "Unknown"]
        .groupby("diag_1_group")
        .agg(admissions=("admission_id", "count"), readmit_30=("readmitted_30_days", "sum"))
        .reset_index()
        .sort_values("admissions", ascending=False)
    )
    g["readmission_rate_pct"] = (g["readmit_30"] / g["admissions"] * 100).round(2)
    return g.head(15)


def build_monthly_trends(fact: pd.DataFrame) -> pd.DataFrame:
    g = fact.groupby(["admission_year", "admission_month", "month_name"]).agg(
        admissions=("admission_id", "count"),
        readmit_30=("readmitted_30_days", "sum"),
        avg_los=("time_in_hospital", "mean"),
    ).reset_index()
    g["readmission_rate_pct"] = (g["readmit_30"] / g["admissions"] * 100).round(2)
    g["avg_los"] = g["avg_los"].round(2)
    return g.sort_values(["admission_year", "admission_month"])


def build_medication_analysis(fact: pd.DataFrame) -> pd.DataFrame:
    rows = []
    full = pd.read_csv(CLEANED_CSV)
    for med in MEDICATION_COLUMNS:
        if med not in full.columns:
            continue
        active = full[med].isin(["Steady", "Up", "Down"])
        subset = full.loc[active, "readmitted_30_days"]
        rows.append({
            "medication_name": med,
            "active_prescriptions": int(active.sum()),
            "readmit_30": int(subset.sum()),
            "admissions_with_med": int(active.sum()),
            "readmission_rate_pct": round(subset.mean() * 100, 2) if active.sum() else 0,
        })
    return pd.DataFrame(rows).sort_values("active_prescriptions", ascending=False)


def build_kpi_summary(fact: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{
        "total_patients": fact["patient_id"].nunique(),
        "total_admissions": len(fact),
        "readmission_rate_pct": round(fact["readmitted_30_days"].mean() * 100, 2),
        "avg_length_of_stay": round(fact["time_in_hospital"].mean(), 2),
        "high_risk_patients": int(fact["high_risk_flag"].eq("Yes").sum()),
        "top_diagnosis": fact["diag_1_group"].value_counts().idxmax(),
        "top_diagnosis_count": int(fact["diag_1_group"].value_counts().iloc[0]),
    }])


def build_high_risk_list(fact: pd.DataFrame) -> pd.DataFrame:
    return (
        fact[fact["risk_tier"].isin(["High", "Critical"])]
        [["patient_id", "admission_id", "gender", "age", "risk_tier",
          "num_medications", "total_prior_visits", "diag_1_group", "readmitted_flag"]]
        .head(5000)
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fact = build_fact_admissions()

    datasets = {
        "fact_admissions": fact,
        "kpi_summary": build_kpi_summary(fact),
        "readmission_by_age": build_readmission_by_age(fact),
        "readmission_by_gender": build_readmission_by_gender(fact),
        "readmission_by_diagnosis": build_readmission_by_diagnosis(fact),
        "monthly_trends": build_monthly_trends(fact),
        "medication_analysis": build_medication_analysis(fact),
        "high_risk_patients": build_high_risk_list(fact),
    }

    for name, df in datasets.items():
        path = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  {name}.csv — {len(df):,} rows")

    # Single-file option for quick import
    fact.to_csv(OUTPUT_DIR / "executive_dashboard_master.csv", index=False)
    print(f"\nAll files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    print("Generating Power BI datasets...")
    main()
