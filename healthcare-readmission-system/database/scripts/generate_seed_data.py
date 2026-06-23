#!/usr/bin/env python
"""Generate normalized CSV seed files and bulk-load SQL from cleaned dataset."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "diabetic_data.csv"
CLEANED_CSV = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
SEEDS_DIR = PROJECT_ROOT / "database" / "seeds" / "csv"

MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide", "tolbutamide",
    "pioglitazone", "rosiglitazone", "acarbose", "miglitol", "troglitazone",
    "tolazamide", "examide", "citoglipton", "insulin",
    "glyburide-metformin", "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone",
]


def _bool_yes(series: pd.Series) -> pd.Series:
    return series.map({"Yes": True, "No": False}).fillna(False).astype(bool)


def generate_patients(df: pd.DataFrame) -> pd.DataFrame:
    """One row per unique patient (latest demographics)."""
    patients = (
        df.sort_values("encounter_id")
        .groupby("patient_nbr", as_index=False)
        .last()[["patient_nbr", "race", "gender", "age", "age_midpoint"]]
        .rename(columns={
            "patient_nbr": "patient_id",
            "age": "age_bracket",
        })
    )
    patients["race"] = patients["race"].fillna("Unknown")
    return patients


def generate_admissions(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "admission_id": df["encounter_id"],
        "patient_id": df["patient_nbr"],
        "admission_type_id": df["admission_type_id"],
        "discharge_disposition_id": df["discharge_disposition_id"],
        "admission_source_id": df["admission_source_id"],
        "time_in_hospital": df["time_in_hospital"],
        "num_lab_procedures": df["num_lab_procedures"],
        "num_procedures": df["num_procedures"],
        "num_medications": df["num_medications"],
        "number_diagnoses": df["number_diagnoses"],
        "medication_changed": df["change"],
        "on_diabetes_med": df["diabetesMed"],
        "readmitted": df["readmitted"],
        "readmitted_30_days": df["readmitted_30_days"].astype(bool),
        "total_prior_visits": df["total_prior_visits"],
        "active_medication_count": df["active_medication_count"],
        "on_insulin": df["on_insulin"],
        "had_prior_inpatient": _bool_yes(df["had_prior_inpatient"]),
        "had_prior_emergency": _bool_yes(df["had_prior_emergency"]),
        "high_utilization_flag": df["high_utilization_flag"].astype(bool),
    })


def generate_diagnosis(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rank_map = [
        (1, "diag_1", "diag_1_group"),
        (2, "diag_2", "diag_2_group"),
        (3, "diag_3", "diag_3_group"),
    ]
    for _, row in df.iterrows():
        for rank, code_col, group_col in rank_map:
            code = row.get(code_col)
            if pd.notna(code) and str(code).strip() not in ("", "nan"):
                rows.append({
                    "admission_id": row["encounter_id"],
                    "patient_id": row["patient_nbr"],
                    "diagnosis_rank": rank,
                    "icd_code": str(code),
                    "icd_group": row.get(group_col, "Unknown"),
                })
    return pd.DataFrame(rows)


def generate_medications(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for med in MEDICATION_COLUMNS:
            status = row.get(med, "No")
            if pd.isna(status):
                status = "No"
            rows.append({
                "admission_id": row["encounter_id"],
                "patient_id": row["patient_nbr"],
                "medication_name": med,
                "dosage_status": status,
            })
    return pd.DataFrame(rows)


def generate_hospital_visits(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    visit_map = [
        ("outpatient", "number_outpatient"),
        ("emergency", "number_emergency"),
        ("inpatient", "number_inpatient"),
    ]
    for _, row in df.iterrows():
        for visit_type, col in visit_map:
            rows.append({
                "admission_id": row["encounter_id"],
                "patient_id": row["patient_nbr"],
                "visit_type": visit_type,
                "visit_count": int(row[col]),
            })
    return pd.DataFrame(rows)


def generate_sample_inserts(patients: pd.DataFrame, admissions: pd.DataFrame, limit: int = 5) -> str:
    """Generate sample INSERT statements for documentation/testing."""
    lines = ["-- Sample INSERT statements (first 5 records)", "SET search_path TO healthcare, public;", ""]
    for _, row in patients.head(limit).iterrows():
        lines.append(
            f"INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) "
            f"VALUES ({row['patient_id']}, '{row['race']}', '{row['gender']}', "
            f"'{row['age_bracket']}', {int(row['age_midpoint'])});"
        )
    lines.append("")
    for _, row in admissions.head(limit).iterrows():
        lines.append(
            f"INSERT INTO admissions (admission_id, patient_id, admission_type_id, "
            f"discharge_disposition_id, admission_source_id, time_in_hospital, "
            f"num_medications, readmitted, readmitted_30_days) VALUES "
            f"({row['admission_id']}, {row['patient_id']}, {row['admission_type_id']}, "
            f"{row['discharge_disposition_id']}, {row['admission_source_id']}, "
            f"{row['time_in_hospital']}, {row['num_medications']}, "
            f"'{row['readmitted']}', {str(row['readmitted_30_days']).upper()});"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    print("Loading source data...")
    raw = pd.read_csv(RAW_CSV, usecols=["encounter_id", "patient_nbr"])
    cleaned = pd.read_csv(CLEANED_CSV)
    df = raw.join(cleaned)

    SEEDS_DIR.mkdir(parents=True, exist_ok=True)

    patients = generate_patients(df)
    admissions = generate_admissions(df)
    diagnosis = generate_diagnosis(df)
    medications = generate_medications(df)
    hospital_visits = generate_hospital_visits(df)

    patients.to_csv(SEEDS_DIR / "patients.csv", index=False)
    admissions.to_csv(SEEDS_DIR / "admissions.csv", index=False)
    diagnosis.to_csv(SEEDS_DIR / "diagnosis.csv", index=False)
    medications.to_csv(SEEDS_DIR / "medications.csv", index=False)
    hospital_visits.to_csv(SEEDS_DIR / "hospital_visits.csv", index=False)

    sample_path = PROJECT_ROOT / "database" / "seeds" / "02_sample_inserts.sql"
    sample_path.write_text(generate_sample_inserts(patients, admissions), encoding="utf-8")

    print(f"patients:        {len(patients):,} rows")
    print(f"admissions:      {len(admissions):,} rows")
    print(f"diagnosis:       {len(diagnosis):,} rows")
    print(f"medications:     {len(medications):,} rows")
    print(f"hospital_visits: {len(hospital_visits):,} rows")
    print(f"CSV output:      {SEEDS_DIR}")
    print(f"Sample SQL:      {sample_path}")


if __name__ == "__main__":
    main()
