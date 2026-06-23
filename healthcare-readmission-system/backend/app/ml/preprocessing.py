"""Preprocessing pipeline for hospital readmission prediction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import (
    AGE_MAP,
    CATEGORICAL_FEATURES,
    CLEANED_CSV,
    HIGH_MISSING_DROP,
    ID_COLUMNS,
    MEDICATION_COLUMNS,
    MISSING_MARKERS,
    NUMERIC_FEATURES,
    ORIGINAL_TARGET,
    PREPROCESSOR_PATH,
    RAW_CSV,
    TARGET_COLUMN,
)
from .data_quality import generate_quality_report, save_quality_report


def load_raw_data(path: Path | str | None = None) -> pd.DataFrame:
    csv_path = Path(path) if path else RAW_CSV
    return pd.read_csv(csv_path)


def _normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object or pd.api.types.is_string_dtype(out[col]):
            out[col] = out[col].replace(list(MISSING_MARKERS), np.nan)
    return out


def _icd_group(code: Any) -> str:
    if pd.isna(code):
        return "Unknown"
    code_str = str(code).strip()
    if not code_str or code_str.lower() in {"nan", "none"}:
        return "Unknown"
    if code_str.startswith("V"):
        return "Supplementary_V"
    if code_str.startswith("E"):
        return "Supplementary_E"
    if code_str.replace(".", "").isdigit() or (len(code_str) >= 3 and code_str[:3].replace(".", "").isdigit()):
        prefix = code_str.replace(".", "")[:3]
        try:
            num = int(prefix)
            if 250 <= num <= 259:
                return "Diabetes_250"
            if 390 <= num <= 459:
                return "Circulatory_390_459"
            if 460 <= num <= 519:
                return "Respiratory_460_519"
            if 520 <= num <= 579:
                return "Digestive_520_579"
            if 800 <= num <= 999:
                return "Injury_800_999"
            return f"Other_{prefix[0]}xx"
        except ValueError:
            return "Other"
    return "Other"


def _count_active_medications(row: pd.Series) -> int:
    active = {"Steady", "Up", "Down"}
    return sum(1 for col in MEDICATION_COLUMNS if col in row.index and row[col] in active)


class HealthcarePreprocessor:
    """
    End-to-end cleaning and feature engineering pipeline.

  Steps:
    1. Normalize missing markers
    2. Remove duplicate clinical records
    3. Drop high-missing / ID columns
    4. Engineer features
    5. Create binary readmission target
    6. Fit/transform sklearn ColumnTransformer for ML
    """

    def __init__(self) -> None:
        self.cleaning_stats: dict[str, Any] = {}
        self.feature_columns: list[str] = []
        self.sklearn_pipeline: Pipeline | None = None
        self._fitted = False

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all cleaning and feature engineering steps."""
        initial_rows = len(df)
        data = _normalize_missing_values(df)

        clinical_cols = [c for c in data.columns if c not in ID_COLUMNS]
        before_dup = len(data)
        data = data.drop_duplicates(subset=clinical_cols, keep="first")
        duplicates_removed = before_dup - len(data)

        drop_cols = [c for c in HIGH_MISSING_DROP + ID_COLUMNS if c in data.columns]
        data = data.drop(columns=drop_cols)

        data["age_midpoint"] = data["age"].map(AGE_MAP).astype("float64")
        data["total_prior_visits"] = (
            data["number_outpatient"]
            + data["number_emergency"]
            + data["number_inpatient"]
        )
        data["active_medication_count"] = data.apply(_count_active_medications, axis=1)
        data["on_insulin"] = np.where(
            data["insulin"].isin(["Steady", "Up", "Down"]), "Yes", "No"
        )
        data["had_prior_inpatient"] = np.where(data["number_inpatient"] > 0, "Yes", "No")
        data["had_prior_emergency"] = np.where(data["number_emergency"] > 0, "Yes", "No")

        for diag_col, group_col in [
            ("diag_1", "diag_1_group"),
            ("diag_2", "diag_2_group"),
            ("diag_3", "diag_3_group"),
        ]:
            if diag_col in data.columns:
                data[group_col] = data[diag_col].apply(_icd_group)

        data[TARGET_COLUMN] = (data[ORIGINAL_TARGET] == "<30").astype(int)

        for col in ["race", "gender", "change", "diabetesMed"]:
            if col in data.columns:
                data[col] = data[col].fillna("Unknown")

        for col in NUMERIC_FEATURES:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        outlier_flags = self._flag_outliers(data)
        data["high_utilization_flag"] = outlier_flags

        self.cleaning_stats = {
            "initial_rows": initial_rows,
            "final_rows": len(data),
            "duplicates_removed": duplicates_removed,
            "columns_dropped": drop_cols,
            "features_engineered": [
                "age_midpoint", "total_prior_visits", "active_medication_count",
                "on_insulin", "had_prior_inpatient", "had_prior_emergency",
                "diag_1_group", "diag_2_group", "diag_3_group", TARGET_COLUMN,
                "high_utilization_flag",
            ],
            "target_positive_rate": round(data[TARGET_COLUMN].mean() * 100, 2),
        }
        return data

    def _flag_outliers(self, df: pd.DataFrame) -> pd.Series:
        """Flag high prior-utilization outliers (IQR method); rows are retained."""
        visit_cols = ["number_outpatient", "number_emergency", "number_inpatient"]
        flags = pd.Series(False, index=df.index)
        for col in visit_cols:
            if col not in df.columns:
                continue
            series = df[col]
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            flags |= series > upper
        return flags.astype(int)

    def build_sklearn_pipeline(self) -> ColumnTransformer:
        numeric_cols = [c for c in NUMERIC_FEATURES if c not in {"admission_type_id", "discharge_disposition_id", "admission_source_id"}]
        id_like_numeric = ["admission_type_id", "discharge_disposition_id", "admission_source_id"]
        cat_cols = CATEGORICAL_FEATURES

        numeric_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        id_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ])
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])

        return ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_cols),
                ("id_cat", id_transformer, id_like_numeric),
                ("cat", categorical_transformer, cat_cols),
            ],
            remainder="drop",
        )

    def fit(self, df: pd.DataFrame) -> "HealthcarePreprocessor":
        cleaned = self.clean(df)
        self.feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
        feature_df = cleaned[self.feature_columns]

        self.sklearn_pipeline = self.build_sklearn_pipeline()
        self.sklearn_pipeline.fit(feature_df)
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self._fitted or self.sklearn_pipeline is None:
            raise RuntimeError("Preprocessor must be fitted before transform().")
        cleaned = self.clean(df)
        return self.sklearn_pipeline.transform(cleaned[self.feature_columns])

    def fit_transform(self, df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        cleaned = self.clean(df)
        self.feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
        feature_df = cleaned[self.feature_columns]

        self.sklearn_pipeline = self.build_sklearn_pipeline()
        matrix = self.sklearn_pipeline.fit_transform(feature_df)
        self._fitted = True
        return cleaned, matrix

    def save(self, path: Path | str | None = None) -> Path:
        save_path = Path(path) if path else PREPROCESSOR_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": self.sklearn_pipeline,
                "feature_columns": self.feature_columns,
                "cleaning_stats": self.cleaning_stats,
            },
            save_path,
        )
        return save_path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "HealthcarePreprocessor":
        load_path = Path(path) if path else PREPROCESSOR_PATH
        payload = joblib.load(load_path)
        obj = cls()
        obj.sklearn_pipeline = payload["pipeline"]
        obj.feature_columns = payload["feature_columns"]
        obj.cleaning_stats = payload.get("cleaning_stats", {})
        obj._fitted = True
        return obj


def run_preprocessing_pipeline(
    raw_path: Path | str | None = None,
    output_csv: Path | str | None = None,
    report_path: Path | str | None = None,
    save_preprocessor: bool = True,
) -> dict[str, Any]:
    """Load raw data, clean, save outputs, and return summary."""
    from .config import QUALITY_REPORT_JSON, REPORTS_DIR

    raw = load_raw_data(raw_path)
    preprocessor = HealthcarePreprocessor()
    cleaned, feature_matrix = preprocessor.fit_transform(raw)

    out_csv = Path(output_csv) if output_csv else CLEANED_CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(out_csv, index=False)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = save_quality_report(raw, report_path or QUALITY_REPORT_JSON)

    if save_preprocessor:
        preprocessor.save()

    summary = {
        "raw_rows": len(raw),
        "cleaned_rows": len(cleaned),
        "cleaned_columns": len(cleaned.columns),
        "feature_matrix_shape": list(feature_matrix.shape),
        "cleaning_stats": preprocessor.cleaning_stats,
        "quality_report_path": str(report_path or QUALITY_REPORT_JSON),
        "cleaned_data_path": str(out_csv),
        "preprocessor_path": str(PREPROCESSOR_PATH) if save_preprocessor else None,
        "target_distribution": report.get("target_distribution"),
    }

    summary_path = REPORTS_DIR / "phase2_cleaning_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
