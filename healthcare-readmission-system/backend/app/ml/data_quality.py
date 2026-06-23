"""Data quality assessment for the Diabetes 130-US Hospitals dataset."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd

from .config import HIGH_MISSING_DROP, ID_COLUMNS, MISSING_MARKERS, NUMERIC_FEATURES


def _normalize_missing(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object or pd.api.types.is_string_dtype(out[col]):
            out[col] = out[col].replace(list(MISSING_MARKERS), np.nan)
    return out


def missing_value_analysis(df: pd.DataFrame) -> dict[str, Any]:
    normalized = _normalize_missing(df)
    total = len(normalized)
    missing = normalized.isna().sum()
    pct = (missing / total * 100).round(2)
    return {
        "total_rows": total,
        "columns_with_missing": int((missing > 0).sum()),
        "by_column": {
            col: {"count": int(missing[col]), "percent": float(pct[col])}
            for col in missing[missing > 0].sort_values(ascending=False).index
        },
        "high_missing_columns_recommended_drop": HIGH_MISSING_DROP,
    }


def duplicate_analysis(df: pd.DataFrame) -> dict[str, Any]:
    clinical_cols = [c for c in df.columns if c not in ID_COLUMNS]
    return {
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "duplicate_encounter_ids": int(df["encounter_id"].duplicated().sum()),
        "duplicate_clinical_records": int(df.duplicated(subset=clinical_cols).sum()),
        "unique_patients": int(df["patient_nbr"].nunique()),
        "repeat_admissions": int(len(df) - df["patient_nbr"].nunique()),
    }


def outlier_analysis(df: pd.DataFrame) -> dict[str, Any]:
    numeric_cols = [
        c for c in [
            "time_in_hospital", "num_lab_procedures", "num_procedures",
            "num_medications", "number_outpatient", "number_emergency",
            "number_inpatient", "number_diagnoses",
        ]
        if c in df.columns
    ]
    results: dict[str, Any] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (series < lower) | (series > upper)
        results[col] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": round(float(series.mean()), 2),
            "median": float(series.median()),
            "q1": float(q1),
            "q3": float(q3),
            "iqr_outlier_count": int(mask.sum()),
            "iqr_outlier_percent": round(float(mask.mean() * 100), 2),
        }
    return results


def target_distribution(df: pd.DataFrame) -> dict[str, Any]:
    if "readmitted" not in df.columns:
        return {}
    counts = df["readmitted"].value_counts(dropna=False).to_dict()
    total = len(df)
    return {
        "raw_counts": {str(k): int(v) for k, v in counts.items()},
        "readmission_within_30_days_rate": round(
            counts.get("<30", 0) / total * 100, 2
        ),
        "class_imbalance_ratio": round(
            counts.get("NO", 0) / max(counts.get("<30", 1), 1), 2
        ),
    }


def generate_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """Run full data quality assessment and return a JSON-serializable report."""
    normalized = _normalize_missing(df)
    return {
        "dataset": "Diabetes 130-US Hospitals (1999-2008)",
        "missing_values": missing_value_analysis(df),
        "duplicates": duplicate_analysis(df),
        "outliers": outlier_analysis(normalized),
        "target_distribution": target_distribution(normalized),
        "data_quality_score": _quality_score(normalized),
        "recommendations": [
            "Replace '?' and 'None' with NaN before analysis.",
            "Drop columns with >40% missing: weight, max_glu_serum, A1Cresult, payer_code, medical_specialty.",
            "Cap extreme prior-visit counts via IQR flags (retain rows; flag for analysis).",
            "Binary target: readmitted within 30 days (<30) vs. not.",
            "Engineer age midpoint, prior visit totals, and ICD diagnosis groups.",
        ],
    }


def _quality_score(df: pd.DataFrame) -> dict[str, Any]:
    normalized = _normalize_missing(df)
    missing_pct = normalized.isna().mean().mean() * 100
    dup_rate = df.duplicated().mean() * 100
    completeness = max(0, 100 - missing_pct)
    uniqueness = max(0, 100 - dup_rate)
    overall = round((completeness * 0.7 + uniqueness * 0.3), 1)
    return {
        "completeness_score": round(completeness, 1),
        "uniqueness_score": round(uniqueness, 1),
        "overall_score": overall,
        "grade": "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D",
    }


def save_quality_report(df: pd.DataFrame, path: str | Any) -> dict[str, Any]:
    report = generate_quality_report(df)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report
