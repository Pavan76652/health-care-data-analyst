-- Performance indexes for analytics and API queries
SET search_path TO healthcare, public;

-- patients
CREATE INDEX IF NOT EXISTS idx_patients_gender ON patients(gender);
CREATE INDEX IF NOT EXISTS idx_patients_age_bracket ON patients(age_bracket);
CREATE INDEX IF NOT EXISTS idx_patients_race ON patients(race);

-- admissions
CREATE INDEX IF NOT EXISTS idx_admissions_patient_id ON admissions(patient_id);
CREATE INDEX IF NOT EXISTS idx_admissions_readmitted_30 ON admissions(readmitted_30_days);
CREATE INDEX IF NOT EXISTS idx_admissions_readmitted ON admissions(readmitted);
CREATE INDEX IF NOT EXISTS idx_admissions_time_in_hospital ON admissions(time_in_hospital);
CREATE INDEX IF NOT EXISTS idx_admissions_admission_type ON admissions(admission_type_id);
CREATE INDEX IF NOT EXISTS idx_admissions_discharge_disposition ON admissions(discharge_disposition_id);
CREATE INDEX IF NOT EXISTS idx_admissions_high_risk ON admissions(readmitted_30_days, high_utilization_flag)
    WHERE readmitted_30_days = TRUE;

-- diagnosis
CREATE INDEX IF NOT EXISTS idx_diagnosis_admission_id ON diagnosis(admission_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_icd_group ON diagnosis(icd_group);
CREATE INDEX IF NOT EXISTS idx_diagnosis_icd_code ON diagnosis(icd_code);
CREATE INDEX IF NOT EXISTS idx_diagnosis_rank ON diagnosis(diagnosis_rank);

-- medications
CREATE INDEX IF NOT EXISTS idx_medications_admission_id ON medications(admission_id);
CREATE INDEX IF NOT EXISTS idx_medications_name ON medications(medication_name);
CREATE INDEX IF NOT EXISTS idx_medications_active ON medications(is_active) WHERE is_active = TRUE;

-- hospital_visits
CREATE INDEX IF NOT EXISTS idx_hospital_visits_admission_id ON hospital_visits(admission_id);
CREATE INDEX IF NOT EXISTS idx_hospital_visits_patient_id ON hospital_visits(patient_id);
CREATE INDEX IF NOT EXISTS idx_hospital_visits_type ON hospital_visits(visit_type);
