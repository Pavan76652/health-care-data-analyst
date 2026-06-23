-- Bulk load normalized seed CSVs into PostgreSQL
-- Run AFTER schema + reference inserts
-- Usage (psql): \i database/seeds/03_bulk_load.sql
-- Or from project root with absolute paths adjusted

SET search_path TO healthcare, public;

-- Truncate in dependency order (for reload)
TRUNCATE hospital_visits, medications, diagnosis, admissions, patients RESTART IDENTITY CASCADE;

\copy patients(patient_id, race, gender, age_bracket, age_midpoint)
    FROM 'database/seeds/csv/patients.csv' WITH (FORMAT csv, HEADER true, NULL '')

\copy admissions(admission_id, patient_id, admission_type_id, discharge_disposition_id,
    admission_source_id, time_in_hospital, num_lab_procedures, num_procedures,
    num_medications, number_diagnoses, medication_changed, on_diabetes_med,
    readmitted, readmitted_30_days, total_prior_visits, active_medication_count,
    on_insulin, had_prior_inpatient, had_prior_emergency, high_utilization_flag)
    FROM 'database/seeds/csv/admissions.csv' WITH (FORMAT csv, HEADER true, NULL '')

\copy diagnosis(admission_id, patient_id, diagnosis_rank, icd_code, icd_group)
    FROM 'database/seeds/csv/diagnosis.csv' WITH (FORMAT csv, HEADER true, NULL '')

\copy medications(admission_id, patient_id, medication_name, dosage_status)
    FROM 'database/seeds/csv/medications.csv' WITH (FORMAT csv, HEADER true, NULL '')

\copy hospital_visits(admission_id, patient_id, visit_type, visit_count)
    FROM 'database/seeds/csv/hospital_visits.csv' WITH (FORMAT csv, HEADER true, NULL '')

-- Verify row counts
SELECT 'patients' AS tbl, COUNT(*) FROM patients
UNION ALL SELECT 'admissions', COUNT(*) FROM admissions
UNION ALL SELECT 'diagnosis', COUNT(*) FROM diagnosis
UNION ALL SELECT 'medications', COUNT(*) FROM medications
UNION ALL SELECT 'hospital_visits', COUNT(*) FROM hospital_visits;
