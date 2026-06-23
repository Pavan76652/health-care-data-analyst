from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_DICTIONARIES = PROJECT_ROOT / "data" / "dictionaries"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_CSV = DATA_RAW / "diabetic_data.csv"
IDS_MAPPING_CSV = DATA_RAW / "IDS_mapping.csv"
CLEANED_CSV = DATA_PROCESSED / "cleaned_data.csv"
QUALITY_REPORT_JSON = REPORTS_DIR / "data_quality_report.json"
METRICS_PATH = MODELS_DIR / "metrics.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.json"
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"

MISSING_MARKERS = ("?", "None", "NULL", "null", "")

# Columns with >40% missing — excluded from modeling (documented in quality report)
HIGH_MISSING_DROP = [
    "weight",
    "max_glu_serum",
    "A1Cresult",
    "payer_code",
    "medical_specialty",
]

ID_COLUMNS = ["encounter_id", "patient_nbr"]

MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide", "tolbutamide",
    "pioglitazone", "rosiglitazone", "acarbose", "miglitol", "troglitazone",
    "tolazamide", "examide", "citoglipton", "insulin",
    "glyburide-metformin", "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone",
]

AGE_MAP = {
    "[0-10)": 5,
    "[10-20)": 15,
    "[20-30)": 25,
    "[30-40)": 35,
    "[40-50)": 45,
    "[50-60)": 55,
    "[60-70)": 65,
    "[70-80)": 75,
    "[80-90)": 85,
    "[90-100)": 95,
}

NUMERIC_FEATURES = [
    "age_midpoint",
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
    "total_prior_visits",
    "active_medication_count",
    "admission_type_id",
    "discharge_disposition_id",
    "admission_source_id",
]

CATEGORICAL_FEATURES = [
    "race",
    "gender",
    "diag_1_group",
    "diag_2_group",
    "diag_3_group",
    "change",
    "diabetesMed",
    "on_insulin",
    "had_prior_inpatient",
    "had_prior_emergency",
]

TARGET_COLUMN = "readmitted_30_days"
ORIGINAL_TARGET = "readmitted"
