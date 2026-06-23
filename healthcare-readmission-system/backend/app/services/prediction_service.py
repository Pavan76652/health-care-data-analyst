from __future__ import annotations

import joblib
import pandas as pd

from app.core.config import settings
from app.schemas.predict import PredictRequest


AGE_BINS = [
    (0, 10, "[0-10)"),
    (10, 20, "[10-20)"),
    (20, 30, "[20-30)"),
    (30, 40, "[30-40)"),
    (40, 50, "[40-50)"),
    (50, 60, "[50-60)"),
    (60, 70, "[60-70)"),
    (70, 80, "[70-80)"),
    (80, 90, "[80-90)"),
    (90, 120, "[90-100)"),
]


def _diagnosis_group(raw: str) -> str:
    txt = (raw or "").strip()
    low = txt.lower()
    if "diab" in low or txt.startswith("250"):
        return "Diabetes_250"
    if "circul" in low or "card" in low:
        return "Circulatory_390_459"
    if "resp" in low or "lung" in low:
        return "Respiratory_460_519"
    if "digest" in low or "gi" in low:
        return "Digestive_520_579"
    if txt.upper().startswith("V"):
        return "Supplementary_V"
    if txt.upper().startswith("E"):
        return "Supplementary_E"
    return "Other_9xx"


def _age_bracket(age: int) -> str:
    for low, high, label in AGE_BINS:
        if low <= age < high:
            return label
    return "[90-100)"


def _recommendation(score: float) -> str:
    if score >= 70:
        return "Initiate intensive discharge planning, 48-hour follow-up call, and pharmacist medication reconciliation."
    if score >= 40:
        return "Schedule early outpatient review within 7 days and provide targeted self-care education."
    return "Standard discharge workflow is sufficient; continue routine monitoring."


def _top_risk_factors(payload: PredictRequest) -> list[str]:
    factors: list[str] = []
    if payload.number_inpatient > 0:
        factors.append("Prior inpatient utilization")
    if payload.number_emergency > 0:
        factors.append("Recent emergency visits")
    if payload.number_of_medications >= 15:
        factors.append("Polypharmacy (15+ medications)")
    if payload.on_insulin:
        factors.append("Insulin-based therapy")
    if payload.time_in_hospital >= 7:
        factors.append("Extended hospital stay")
    if payload.age >= 70:
        factors.append("Advanced age")
    return factors[:5] or ["No strong risk factors detected from submitted profile"]


def _to_model_features(payload: PredictRequest) -> dict:
    total_prior_visits = payload.number_outpatient + payload.number_emergency + payload.number_inpatient
    active_medication_count = 1 if payload.diabetes_med else 0

    return {
        "age_midpoint": float(payload.age),
        "time_in_hospital": payload.time_in_hospital,
        "num_lab_procedures": payload.num_lab_procedures,
        "num_procedures": payload.number_of_procedures,
        "num_medications": payload.number_of_medications,
        "number_outpatient": payload.number_outpatient,
        "number_emergency": payload.number_emergency,
        "number_inpatient": payload.number_inpatient,
        "number_diagnoses": payload.number_diagnoses,
        "total_prior_visits": total_prior_visits,
        "active_medication_count": active_medication_count,
        "admission_type_id": payload.admission_type_id,
        "discharge_disposition_id": payload.discharge_disposition_id,
        "admission_source_id": payload.admission_source_id,
        "race": payload.race,
        "gender": payload.gender,
        "diag_1_group": _diagnosis_group(payload.diagnosis),
        "diag_2_group": "Unknown",
        "diag_3_group": "Unknown",
        "change": "Ch" if payload.diabetes_med else "No",
        "diabetesMed": "Yes" if payload.diabetes_med else "No",
        "on_insulin": "Yes" if payload.on_insulin else "No",
        "had_prior_inpatient": "Yes" if payload.number_inpatient > 0 else "No",
        "had_prior_emergency": "Yes" if payload.number_emergency > 0 else "No",
        "age": _age_bracket(payload.age),
    }


def predict(payload: PredictRequest) -> dict:
    if not settings.best_model_path.exists():
        raise FileNotFoundError(f"Model not found at {settings.best_model_path}")

    bundle = joblib.load(settings.best_model_path)
    preprocessor = bundle["preprocessor"]
    classifier = bundle["classifier"]
    features = _to_model_features(payload)
    x = pd.DataFrame([features])[preprocessor.feature_columns]
    x_t = preprocessor.sklearn_pipeline.transform(x)
    probability = float(classifier.predict_proba(x_t)[0, 1])
    risk_score = round(probability * 100, 1)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "readmission_probability": round(probability, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": _recommendation(risk_score),
        "top_risk_factors": _top_risk_factors(payload),
    }
