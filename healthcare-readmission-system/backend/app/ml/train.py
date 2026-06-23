"""Machine learning training pipeline for 30-day readmission prediction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from xgboost import XGBClassifier

from .config import (
    BEST_MODEL_PATH,
    CATEGORICAL_FEATURES,
    CLEANED_CSV,
    FEATURE_IMPORTANCE_PATH,
    METRICS_PATH,
    MODELS_DIR,
    NUMERIC_FEATURES,
    REPORTS_DIR,
    TARGET_COLUMN,
)
from .evaluation import compute_metrics, cv_summary
from .preprocessing import HealthcarePreprocessor, load_raw_data

MODEL_COMPARISON_PATH = REPORTS_DIR / "model_comparison.json"
RANDOM_STATE = 42


def _get_feature_names(preprocessor: HealthcarePreprocessor) -> list[str]:
    if preprocessor.sklearn_pipeline is None:
        return []
    try:
        return list(preprocessor.sklearn_pipeline.get_feature_names_out())
    except Exception:
        return NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _extract_importance(
    model_name: str,
    model: Any,
    feature_names: list[str],
) -> dict[str, float]:
    if model_name == "logistic_regression":
        coefs = np.abs(model.coef_[0])
    elif hasattr(model, "feature_importances_"):
        coefs = model.feature_importances_
    else:
        return {}

    if len(feature_names) != len(coefs):
        feature_names = [f"feature_{i}" for i in range(len(coefs))]

    pairs = sorted(zip(feature_names, coefs), key=lambda x: x[1], reverse=True)
    return {name: round(float(val), 6) for name, val in pairs[:25]}


def prepare_data(
    data_path: Path | str | None = None,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, HealthcarePreprocessor]:
    """Clean data, split train/test, fit preprocessor on train only."""
    if data_path and Path(data_path).suffix == ".csv" and "cleaned" in str(data_path):
        df = pd.read_csv(data_path)
        preprocessor = HealthcarePreprocessor()
        cleaned = preprocessor.clean(df)
    else:
        raw = load_raw_data(data_path)
        preprocessor = HealthcarePreprocessor()
        cleaned = preprocessor.clean(raw)

    y = cleaned[TARGET_COLUMN].values
    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X_df = cleaned[feature_cols]

    X_train_df, X_test_df, y_train, y_test = train_test_split(
        X_df, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y,
    )

    preprocessor.sklearn_pipeline = preprocessor.build_sklearn_pipeline()
    X_train = preprocessor.sklearn_pipeline.fit_transform(X_train_df)
    X_test = preprocessor.sklearn_pipeline.transform(X_test_df)
    preprocessor._fitted = True
    preprocessor.feature_columns = feature_cols

    train_cleaned = cleaned.loc[X_train_df.index]
    test_cleaned = cleaned.loc[X_test_df.index]
    return train_cleaned, test_cleaned, X_train, X_test, y_train, y_test, preprocessor


def get_model_configs() -> dict[str, Any]:
    pos_weight = 4.83  # approximate class imbalance from EDA
    return {
        "logistic_regression": {
            "estimator": LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
            "params": {
                "C": [0.01, 0.1, 1.0, 10.0],
                "solver": ["lbfgs", "saga"],
                "penalty": ["l2"],
            },
        },
        "random_forest": {
            "estimator": RandomForestClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 15, 20, None],
                "min_samples_leaf": [1, 3, 5],
                "max_features": ["sqrt", "log2"],
            },
        },
        "xgboost": {
            "estimator": XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                scale_pos_weight=pos_weight,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                verbosity=0,
            ),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [4, 6, 8],
                "learning_rate": [0.01, 0.05, 0.1],
                "subsample": [0.8, 1.0],
                "colsample_bytree": [0.8, 1.0],
            },
        },
    }


def train_and_tune_model(
    name: str,
    config: dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    cv_folds: int = 3,
    n_iter: int = 12,
) -> tuple[Any, dict[str, Any], dict[str, float]]:
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)

    search = RandomizedSearchCV(
        estimator=config["estimator"],
        param_distributions=config["params"],
        n_iter=n_iter,
        scoring="roc_auc",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)

    cv_scores = cross_validate(
        search.best_estimator_,
        X_train,
        y_train,
        cv=cv,
        scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
        n_jobs=-1,
    )

    tuning_result = {
        "best_params": search.best_params_,
        "best_cv_roc_auc": round(float(search.best_score_), 4),
        "cv_metrics": cv_summary({
            "accuracy": cv_scores["test_accuracy"].tolist(),
            "precision": cv_scores["test_precision"].tolist(),
            "recall": cv_scores["test_recall"].tolist(),
            "f1_score": cv_scores["test_f1"].tolist(),
            "roc_auc": cv_scores["test_roc_auc"].tolist(),
        }),
    }
    return search.best_estimator_, tuning_result, tuning_result["cv_metrics"]


def run_training_pipeline(
    data_path: Path | str | None = None,
    test_size: float = 0.2,
    cv_folds: int = 3,
    n_iter: int = 12,
) -> dict[str, Any]:
    """Train all models, compare metrics, save best model."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    _, _, X_train, X_test, y_train, y_test, preprocessor = prepare_data(
        data_path or CLEANED_CSV, test_size=test_size,
    )
    feature_names = _get_feature_names(preprocessor)

    results: dict[str, Any] = {}
    best_model_name = ""
    best_roc_auc = -1.0
    best_estimator = None

    for name, config in get_model_configs().items():
        print(f"Training {name}...")
        estimator, tuning, cv_metrics = train_and_tune_model(
            name, config, X_train, y_train, cv_folds=cv_folds, n_iter=n_iter,
        )

        y_pred = estimator.predict(X_test)
        y_proba = estimator.predict_proba(X_test)[:, 1]
        test_metrics = compute_metrics(y_test, y_pred, y_proba)
        importance = _extract_importance(name, estimator, feature_names)

        results[name] = {
            "best_params": tuning["best_params"],
            "cv_metrics": cv_metrics,
            "test_metrics": test_metrics,
            "top_features": dict(list(importance.items())[:10]),
        }

        roc = test_metrics.get("roc_auc") or 0
        if roc > best_roc_auc:
            best_roc_auc = roc
            best_model_name = name
            best_estimator = estimator

        print(f"  Test ROC-AUC: {roc:.4f} | F1: {test_metrics['f1_score']:.4f}")

    assert best_estimator is not None

    # Save best model bundle (preprocessor + classifier)
    model_bundle = {
        "model_name": best_model_name,
        "preprocessor": preprocessor,
        "classifier": best_estimator,
        "feature_names": feature_names,
        "target": TARGET_COLUMN,
    }
    joblib.dump(model_bundle, BEST_MODEL_PATH)
    preprocessor.save()

    # Feature importance for best model
    best_importance = _extract_importance(best_model_name, best_estimator, feature_names)
    with open(FEATURE_IMPORTANCE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "model": best_model_name,
            "importance": best_importance,
        }, f, indent=2)

    summary = {
        "best_model": best_model_name,
        "best_test_roc_auc": best_roc_auc,
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "models": results,
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(MODEL_COMPARISON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def predict_risk_score(patient_features: dict[str, Any], bundle_path: Path | str | None = None) -> dict[str, Any]:
    """Predict readmission probability and risk score 0-100."""
    bundle = joblib.load(bundle_path or BEST_MODEL_PATH)
    preprocessor: HealthcarePreprocessor = bundle["preprocessor"]
    classifier = bundle["classifier"]

    df = pd.DataFrame([patient_features])
    X = preprocessor.sklearn_pipeline.transform(df[preprocessor.feature_columns])
    proba = float(classifier.predict_proba(X)[0, 1])
    risk_score = round(proba * 100, 1)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "readmission_probability": round(proba, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
    }
