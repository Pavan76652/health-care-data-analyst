from __future__ import annotations

from functools import lru_cache

import pandas as pd

from app.core.config import settings


@lru_cache(maxsize=1)
def load_fact_admissions() -> pd.DataFrame:
    path = settings.dashboard_data_dir / "fact_admissions.csv"
    return pd.read_csv(path)


def get_patients(page: int = 1, page_size: int = 25, search: str | None = None) -> dict:
    df = load_fact_admissions()
    if search:
        search_l = search.lower().strip()
        mask = (
            df["patient_id"].astype(str).str.contains(search_l, na=False)
            | df["gender"].astype(str).str.lower().str.contains(search_l, na=False)
            | df["diag_1_group"].astype(str).str.lower().str.contains(search_l, na=False)
        )
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end].copy()
    rows = page_df[
        [
            "patient_id",
            "admission_id",
            "gender",
            "age",
            "diag_1_group",
            "time_in_hospital",
            "num_medications",
            "readmitted_flag",
            "risk_tier",
        ]
    ].to_dict(orient="records")

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total,
        "items": rows,
    }


def get_analytics_summary() -> dict:
    df = load_fact_admissions()
    readmit_rate = float(df["readmitted_30_days"].mean() * 100)

    by_age = (
        df.groupby("age", dropna=False)["readmitted_30_days"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "admissions", "mean": "readmission_rate"})
    )
    by_age["readmission_rate"] = (by_age["readmission_rate"] * 100).round(2)

    top_diag = (
        df.groupby("diag_1_group")["readmitted_30_days"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "admissions", "mean": "readmission_rate"})
        .sort_values("admissions", ascending=False)
        .head(10)
    )
    top_diag["readmission_rate"] = (top_diag["readmission_rate"] * 100).round(2)

    return {
        "kpis": {
            "total_patients": int(df["patient_id"].nunique()),
            "total_admissions": int(len(df)),
            "readmission_rate_30_day_pct": round(readmit_rate, 2),
            "average_length_of_stay": round(float(df["time_in_hospital"].mean()), 2),
            "high_risk_patients": int((df["high_risk_flag"] == "Yes").sum()),
        },
        "readmission_by_age": by_age.to_dict(orient="records"),
        "top_diagnoses": top_diag.to_dict(orient="records"),
    }


def get_dashboard_payload() -> dict:
    data_dir = settings.dashboard_data_dir
    kpi = pd.read_csv(data_dir / "kpi_summary.csv").iloc[0].to_dict()
    by_age = pd.read_csv(data_dir / "readmission_by_age.csv").to_dict(orient="records")
    by_gender = pd.read_csv(data_dir / "readmission_by_gender.csv").to_dict(orient="records")
    by_diag = pd.read_csv(data_dir / "readmission_by_diagnosis.csv").to_dict(orient="records")
    monthly = pd.read_csv(data_dir / "monthly_trends.csv").to_dict(orient="records")
    meds = pd.read_csv(data_dir / "medication_analysis.csv").head(15).to_dict(orient="records")

    return {
        "kpis": kpi,
        "charts": {
            "readmission_by_age": by_age,
            "readmission_by_gender": by_gender,
            "readmission_by_diagnosis": by_diag,
            "monthly_trends": monthly,
            "medication_analysis": meds,
        },
    }
