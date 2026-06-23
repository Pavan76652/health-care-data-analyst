-- Analytics views for dashboards and reporting
SET search_path TO healthcare, public;

-- -----------------------------------------------------------------------------
-- v_readmission_summary — KPI-level metrics
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_readmission_summary AS
SELECT
    COUNT(DISTINCT p.patient_id)                              AS total_patients,
    COUNT(a.admission_id)                                     AS total_admissions,
    ROUND(AVG(a.time_in_hospital)::numeric, 2)                AS avg_length_of_stay,
    ROUND(
        100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*),
        2
    )                                                         AS readmission_rate_30_day_pct,
    SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)     AS readmissions_within_30_days,
    SUM(CASE WHEN a.high_utilization_flag THEN 1 ELSE 0 END)  AS high_utilization_admissions
FROM admissions a
JOIN patients p ON a.patient_id = p.patient_id;

-- -----------------------------------------------------------------------------
-- v_readmission_by_demographics
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_readmission_by_demographics AS
SELECT
    p.gender,
    p.age_bracket,
    p.race,
    COUNT(a.admission_id)                                     AS admission_count,
    SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)     AS readmit_30_count,
    ROUND(
        100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*),
        2
    )                                                         AS readmission_rate_pct
FROM admissions a
JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.gender, p.age_bracket, p.race;

-- -----------------------------------------------------------------------------
-- v_readmission_by_diagnosis
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_readmission_by_diagnosis AS
SELECT
    d.icd_group,
    d.diagnosis_rank,
    COUNT(DISTINCT a.admission_id)                            AS admission_count,
    SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)     AS readmit_30_count,
    ROUND(
        100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)
            / NULLIF(COUNT(DISTINCT a.admission_id), 0),
        2
    )                                                         AS readmission_rate_pct
FROM diagnosis d
JOIN admissions a ON d.admission_id = a.admission_id
WHERE d.icd_group IS NOT NULL AND d.icd_group <> 'Unknown'
GROUP BY d.icd_group, d.diagnosis_rank;

-- -----------------------------------------------------------------------------
-- v_medication_analysis
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_medication_analysis AS
SELECT
    m.medication_name,
    m.dosage_status,
    COUNT(*)                                                  AS prescription_count,
    COUNT(DISTINCT m.admission_id)                            AS admission_count,
    ROUND(
        100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)
            / NULLIF(COUNT(DISTINCT m.admission_id), 0),
        2
    )                                                         AS readmission_rate_pct
FROM medications m
JOIN admissions a ON m.admission_id = a.admission_id
GROUP BY m.medication_name, m.dosage_status;

-- -----------------------------------------------------------------------------
-- v_patient_admission_detail — full encounter detail for API
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_patient_admission_detail AS
SELECT
    p.patient_id,
    p.race,
    p.gender,
    p.age_bracket,
    p.age_midpoint,
    a.admission_id,
    rat.description       AS admission_type,
    rds.description       AS discharge_disposition,
    ras.description       AS admission_source,
    a.time_in_hospital,
    a.num_medications,
    a.num_procedures,
    a.readmitted,
    a.readmitted_30_days,
    a.total_prior_visits,
    a.high_utilization_flag,
    d1.icd_code           AS primary_diagnosis_code,
    d1.icd_group          AS primary_diagnosis_group
FROM patients p
JOIN admissions a ON p.patient_id = a.patient_id
LEFT JOIN ref_admission_type rat ON a.admission_type_id = rat.admission_type_id
LEFT JOIN ref_discharge_disposition rds ON a.discharge_disposition_id = rds.discharge_disposition_id
LEFT JOIN ref_admission_source ras ON a.admission_source_id = ras.admission_source_id
LEFT JOIN diagnosis d1 ON a.admission_id = d1.admission_id AND d1.diagnosis_rank = 1;

-- -----------------------------------------------------------------------------
-- v_high_risk_patients — actionable discharge list
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_high_risk_patients AS
SELECT
    p.patient_id,
    a.admission_id,
    p.gender,
    p.age_bracket,
    a.time_in_hospital,
    a.num_medications,
    a.total_prior_visits,
    d.icd_group           AS primary_diagnosis,
    CASE
        WHEN a.total_prior_visits >= 5 AND a.num_medications >= 20 THEN 'Critical'
        WHEN a.total_prior_visits >= 3 OR a.num_medications >= 15 THEN 'High'
        WHEN a.had_prior_inpatient OR a.had_prior_emergency THEN 'Moderate'
        ELSE 'Low'
    END                   AS risk_tier
FROM patients p
JOIN admissions a ON p.patient_id = a.patient_id
LEFT JOIN diagnosis d ON a.admission_id = d.admission_id AND d.diagnosis_rank = 1
WHERE a.high_utilization_flag = TRUE
   OR a.total_prior_visits >= 3
   OR a.num_medications >= 15;

-- -----------------------------------------------------------------------------
-- v_utilization_summary
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_utilization_summary AS
SELECT
    hv.visit_type,
    SUM(hv.visit_count)                                       AS total_visits,
    ROUND(AVG(hv.visit_count)::numeric, 2)                    AS avg_visits_per_admission,
    MAX(hv.visit_count)                                       AS max_visits
FROM hospital_visits hv
GROUP BY hv.visit_type;
