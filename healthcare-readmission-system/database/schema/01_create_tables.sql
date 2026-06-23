-- =============================================================================
-- Healthcare Readmission System — PostgreSQL Schema
-- Dataset: Diabetes 130-US Hospitals (1999-2008)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS healthcare;
SET search_path TO healthcare, public;

-- -----------------------------------------------------------------------------
-- Reference / lookup tables (from IDS_mapping)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ref_admission_type (
    admission_type_id   SMALLINT PRIMARY KEY,
    description         VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_discharge_disposition (
    discharge_disposition_id SMALLINT PRIMARY KEY,
    description              VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_admission_source (
    admission_source_id SMALLINT PRIMARY KEY,
    description         VARCHAR(120) NOT NULL
);

-- -----------------------------------------------------------------------------
-- patients
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id      BIGINT PRIMARY KEY,
    race            VARCHAR(50),
    gender          VARCHAR(20) NOT NULL,
    age_bracket     VARCHAR(20) NOT NULL,
    age_midpoint    SMALLINT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE patients IS 'Unique diabetic patients across all hospital encounters';

-- -----------------------------------------------------------------------------
-- admissions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admissions (
    admission_id                BIGINT PRIMARY KEY,
    patient_id                  BIGINT NOT NULL REFERENCES patients(patient_id),
    admission_type_id           SMALLINT REFERENCES ref_admission_type(admission_type_id),
    discharge_disposition_id    SMALLINT REFERENCES ref_discharge_disposition(discharge_disposition_id),
    admission_source_id         SMALLINT REFERENCES ref_admission_source(admission_source_id),
    time_in_hospital            SMALLINT NOT NULL CHECK (time_in_hospital BETWEEN 1 AND 14),
    num_lab_procedures          SMALLINT DEFAULT 0,
    num_procedures              SMALLINT DEFAULT 0,
    num_medications             SMALLINT DEFAULT 0,
    number_diagnoses            SMALLINT DEFAULT 1,
    medication_changed          VARCHAR(5),
    on_diabetes_med             VARCHAR(5),
    readmitted                  VARCHAR(10) NOT NULL,
    readmitted_30_days          BOOLEAN NOT NULL DEFAULT FALSE,
    total_prior_visits          SMALLINT DEFAULT 0,
    active_medication_count     SMALLINT DEFAULT 0,
    on_insulin                  VARCHAR(5),
    had_prior_inpatient         BOOLEAN DEFAULT FALSE,
    had_prior_emergency         BOOLEAN DEFAULT FALSE,
    high_utilization_flag       BOOLEAN DEFAULT FALSE,
    admission_date              DATE,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE admissions IS 'Hospital inpatient encounters; one row per admission';

-- -----------------------------------------------------------------------------
-- diagnosis
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnosis (
    diagnosis_id        BIGSERIAL PRIMARY KEY,
    admission_id        BIGINT NOT NULL REFERENCES admissions(admission_id) ON DELETE CASCADE,
    patient_id          BIGINT NOT NULL REFERENCES patients(patient_id),
    diagnosis_rank      SMALLINT NOT NULL CHECK (diagnosis_rank BETWEEN 1 AND 3),
    icd_code            VARCHAR(20),
    icd_group           VARCHAR(50),
    UNIQUE (admission_id, diagnosis_rank)
);

COMMENT ON TABLE diagnosis IS 'ICD-9 diagnosis codes per admission (primary, secondary, tertiary)';

-- -----------------------------------------------------------------------------
-- medications
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medications (
    medication_id       BIGSERIAL PRIMARY KEY,
    admission_id        BIGINT NOT NULL REFERENCES admissions(admission_id) ON DELETE CASCADE,
    patient_id          BIGINT NOT NULL REFERENCES patients(patient_id),
    medication_name     VARCHAR(60) NOT NULL,
    dosage_status       VARCHAR(10) NOT NULL CHECK (dosage_status IN ('No', 'Steady', 'Up', 'Down')),
    is_active           BOOLEAN GENERATED ALWAYS AS (dosage_status IN ('Steady', 'Up', 'Down')) STORED
);

COMMENT ON TABLE medications IS 'Diabetes-related medications administered during admission';

-- -----------------------------------------------------------------------------
-- hospital_visits (prior-year utilization linked to admission)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hospital_visits (
    visit_id            BIGSERIAL PRIMARY KEY,
    admission_id        BIGINT NOT NULL REFERENCES admissions(admission_id) ON DELETE CASCADE,
    patient_id          BIGINT NOT NULL REFERENCES patients(patient_id),
    visit_type          VARCHAR(20) NOT NULL CHECK (visit_type IN ('outpatient', 'emergency', 'inpatient')),
    visit_count         SMALLINT NOT NULL DEFAULT 0 CHECK (visit_count >= 0),
    UNIQUE (admission_id, visit_type)
);

COMMENT ON TABLE hospital_visits IS 'Prior-year healthcare utilization counts before each admission';
