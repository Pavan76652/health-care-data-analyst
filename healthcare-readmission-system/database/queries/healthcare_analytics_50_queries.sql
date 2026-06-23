-- =============================================================================
-- 50 Healthcare Analytics SQL Queries
-- Schema: healthcare | Dataset: Diabetes 130-US Hospitals
-- =============================================================================
SET search_path TO healthcare, public;

-- =============================================================================
-- DEMOGRAPHICS & READMISSION (Queries 1–10)
-- =============================================================================

-- Q1: Most readmitted age groups
SELECT p.age_bracket,
       COUNT(*) AS admissions,
       SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) AS readmit_30,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS rate_pct
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.age_bracket, p.age_midpoint
ORDER BY rate_pct DESC;

-- Q2: Readmission rate by gender
SELECT p.gender,
       COUNT(*) AS admissions,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_rate_pct
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.gender;

-- Q3: Readmission rate by race
SELECT p.race,
       COUNT(*) AS admissions,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_rate_pct
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.race
ORDER BY readmit_rate_pct DESC;

-- Q4: Gender × age readmission cross-tab
SELECT p.gender, p.age_bracket,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS rate_pct
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.gender, p.age_bracket
ORDER BY rate_pct DESC;

-- Q5: Total unique patients
SELECT COUNT(DISTINCT patient_id) AS total_patients FROM patients;

-- Q6: Patients with multiple admissions
SELECT COUNT(*) AS repeat_patients
FROM (SELECT patient_id FROM admissions GROUP BY patient_id HAVING COUNT(*) > 1) t;

-- Q7: Average admissions per patient
SELECT ROUND(COUNT(*)::numeric / COUNT(DISTINCT patient_id), 2) AS avg_admissions_per_patient
FROM admissions;

-- Q8: Readmission outcome distribution (all categories)
SELECT readmitted, COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM admissions GROUP BY readmitted;

-- Q9: Female vs male 30-day readmission comparison
SELECT p.gender,
       SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) AS readmit_count,
       COUNT(*) - SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) AS no_readmit_count
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.gender;

-- Q10: Highest-risk age-gender segment
SELECT p.gender, p.age_bracket,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS rate_pct
FROM admissions a JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.gender, p.age_bracket
HAVING COUNT(*) >= 500
ORDER BY rate_pct DESC LIMIT 5;

-- =============================================================================
-- LENGTH OF STAY & ADMISSION METRICS (Queries 11–18)
-- =============================================================================

-- Q11: Average length of stay (days)
SELECT ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los FROM admissions;

-- Q12: LOS by readmission status
SELECT readmitted_30_days,
       ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los,
       MIN(time_in_hospital) AS min_los,
       MAX(time_in_hospital) AS max_los
FROM admissions GROUP BY readmitted_30_days;

-- Q13: LOS distribution
SELECT time_in_hospital AS days, COUNT(*) AS admissions
FROM admissions GROUP BY time_in_hospital ORDER BY days;

-- Q14: Admission type breakdown
SELECT rat.description, COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions a
JOIN ref_admission_type rat ON a.admission_type_id = rat.admission_type_id
GROUP BY rat.description ORDER BY n DESC;

-- Q15: Discharge disposition analysis
SELECT rds.description, COUNT(*) AS n
FROM admissions a
JOIN ref_discharge_disposition rds ON a.discharge_disposition_id = rds.discharge_disposition_id
GROUP BY rds.description ORDER BY n DESC LIMIT 10;

-- Q16: Admission source analysis
SELECT ras.description, COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions a
JOIN ref_admission_source ras ON a.admission_source_id = ras.admission_source_id
GROUP BY ras.description ORDER BY readmit_pct DESC;

-- Q17: Long stays (7+ days) readmission rate
SELECT CASE WHEN time_in_hospital >= 7 THEN '7+ days' ELSE '<7 days' END AS stay_group,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY 1;

-- Q18: Average lab procedures per admission
SELECT ROUND(AVG(num_lab_procedures)::numeric, 2) AS avg_lab_procedures FROM admissions;

-- =============================================================================
-- DIAGNOSIS ANALYSIS (Queries 19–26)
-- =============================================================================

-- Q19: Diagnosis causing maximum readmission (primary)
SELECT d.icd_group,
       COUNT(DISTINCT a.admission_id) AS admissions,
       SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) AS readmit_30,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)
           / NULLIF(COUNT(DISTINCT a.admission_id), 0), 2) AS rate_pct
FROM diagnosis d JOIN admissions a ON d.admission_id = a.admission_id
WHERE d.diagnosis_rank = 1 AND d.icd_group <> 'Unknown'
GROUP BY d.icd_group ORDER BY readmit_30 DESC LIMIT 10;

-- Q20: Top 10 primary ICD codes by volume
SELECT d.icd_code, COUNT(*) AS n
FROM diagnosis d WHERE d.diagnosis_rank = 1
GROUP BY d.icd_code ORDER BY n DESC LIMIT 10;

-- Q21: Readmission rate by number of diagnoses
SELECT number_diagnoses,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY number_diagnoses ORDER BY number_diagnoses;

-- Q22: Diabetes (250) primary diagnosis readmission rate
SELECT ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS diabetes_readmit_pct
FROM diagnosis d JOIN admissions a ON d.admission_id = a.admission_id
WHERE d.diagnosis_rank = 1 AND d.icd_group = 'Diabetes_250';

-- Q23: Circulatory disease readmission rate
SELECT ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS circulatory_readmit_pct
FROM diagnosis d JOIN admissions a ON d.admission_id = a.admission_id
WHERE d.diagnosis_rank = 1 AND d.icd_group = 'Circulatory_390_459';

-- Q24: Secondary diagnosis impact on readmission
SELECT d.icd_group,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS rate_pct
FROM diagnosis d JOIN admissions a ON d.admission_id = a.admission_id
WHERE d.diagnosis_rank = 2 AND d.icd_group <> 'Unknown'
GROUP BY d.icd_group ORDER BY rate_pct DESC LIMIT 10;

-- Q25: Admissions with 3 diagnoses vs 1
SELECT CASE WHEN number_diagnoses >= 3 THEN '3+' ELSE '1-2' END AS diag_group,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY 1;

-- Q26: Most common diagnosis pairs (primary + secondary)
SELECT d1.icd_group AS primary_grp, d2.icd_group AS secondary_grp, COUNT(*) AS n
FROM diagnosis d1
JOIN diagnosis d2 ON d1.admission_id = d2.admission_id AND d2.diagnosis_rank = 2
WHERE d1.diagnosis_rank = 1
GROUP BY d1.icd_group, d2.icd_group ORDER BY n DESC LIMIT 10;

-- =============================================================================
-- MEDICATION ANALYSIS (Queries 27–34)
-- =============================================================================

-- Q27: Medication analysis — active prescriptions by drug
SELECT medication_name,
       SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_count,
       COUNT(*) AS total_records
FROM medications GROUP BY medication_name ORDER BY active_count DESC;

-- Q28: Insulin usage and readmission
SELECT a.on_insulin,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions a GROUP BY a.on_insulin;

-- Q29: Readmission by number of medications
SELECT CASE
         WHEN num_medications <= 10 THEN '1-10'
         WHEN num_medications <= 20 THEN '11-20'
         ELSE '21+'
       END AS med_group,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY 1 ORDER BY med_group;

-- Q30: Medication changes and readmission
SELECT medication_changed,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY medication_changed;

-- Q31: Diabetes med flag vs readmission
SELECT on_diabetes_med,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY on_diabetes_med;

-- Q32: Metformin active patients readmission rate
SELECT ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(DISTINCT a.admission_id), 2) AS readmit_pct
FROM medications m
JOIN admissions a ON m.admission_id = a.admission_id
WHERE m.medication_name = 'metformin' AND m.is_active = TRUE;

-- Q33: Most prescribed medication combinations (top insulin + oral)
SELECT COUNT(DISTINCT a.admission_id) AS admissions_on_insulin
FROM medications m JOIN admissions a ON m.admission_id = a.admission_id
WHERE m.medication_name = 'insulin' AND m.dosage_status IN ('Steady', 'Up', 'Down');

-- Q34: Average active medications per admission
SELECT ROUND(AVG(active_medication_count)::numeric, 2) AS avg_active_meds FROM admissions;

-- =============================================================================
-- PRIOR UTILIZATION / HOSPITAL VISITS (Queries 35–40)
-- =============================================================================

-- Q35: Prior outpatient visits vs readmission
SELECT CASE WHEN hv.visit_count = 0 THEN '0' WHEN hv.visit_count <= 2 THEN '1-2' ELSE '3+' END AS visits,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM hospital_visits hv
JOIN admissions a ON hv.admission_id = a.admission_id
WHERE hv.visit_type = 'outpatient'
GROUP BY 1;

-- Q36: Prior emergency visits impact
SELECT hv.visit_count AS er_visits,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM hospital_visits hv
JOIN admissions a ON hv.admission_id = a.admission_id
WHERE hv.visit_type = 'emergency' AND hv.visit_count <= 5
GROUP BY hv.visit_count ORDER BY hv.visit_count;

-- Q37: Prior inpatient visits and readmission
SELECT CASE WHEN hv.visit_count > 0 THEN 'Had prior inpatient' ELSE 'No prior inpatient' END AS grp,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM hospital_visits hv
JOIN admissions a ON hv.admission_id = a.admission_id
WHERE hv.visit_type = 'inpatient'
GROUP BY 1;

-- Q38: Total prior visits vs readmission
SELECT CASE
         WHEN total_prior_visits = 0 THEN '0'
         WHEN total_prior_visits <= 3 THEN '1-3'
         ELSE '4+'
       END AS prior_visits,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY 1;

-- Q39: High utilization flag readmission rate
SELECT high_utilization_flag,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY high_utilization_flag;

-- Q40: Average prior visits by readmission status
SELECT readmitted_30_days, ROUND(AVG(total_prior_visits)::numeric, 2) AS avg_prior_visits
FROM admissions GROUP BY readmitted_30_days;

-- =============================================================================
-- CLINICAL PROCEDURES & RISK (Queries 41–46)
-- =============================================================================

-- Q41: Procedures count vs readmission
SELECT num_procedures,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY num_procedures ORDER BY num_procedures;

-- Q42: High-risk patients count (from view)
SELECT risk_tier, COUNT(*) AS n FROM v_high_risk_patients GROUP BY risk_tier;

-- Q43: Dashboard KPIs (single row)
SELECT * FROM v_readmission_summary;

-- Q44: Top 5 diagnoses by readmission rate (min 1000 admissions)
SELECT icd_group, admission_count, readmission_rate_pct
FROM v_readmission_by_diagnosis
WHERE diagnosis_rank = 1 AND admission_count >= 1000
ORDER BY readmission_rate_pct DESC LIMIT 5;

-- Q45: Patients with 3+ admissions and any 30-day readmit
SELECT COUNT(DISTINCT patient_id) AS frequent_readmit_patients
FROM (
    SELECT patient_id, SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) AS readmit_count
    FROM admissions GROUP BY patient_id
    HAVING COUNT(*) >= 3 AND SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) >= 1
) t;

-- Q46: Correlation proxy — LOS vs medications for readmitted patients
SELECT readmitted_30_days,
       ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los,
       ROUND(AVG(num_medications)::numeric, 2) AS avg_meds
FROM admissions GROUP BY readmitted_30_days;

-- =============================================================================
-- OPERATIONAL & TREND QUERIES (Queries 47–50)
-- =============================================================================

-- Q47: Monthly admission trend (synthetic month from admission_id hash)
SELECT (admission_id % 12) + 1 AS month_bucket,
       COUNT(*) AS admissions,
       ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions GROUP BY 1 ORDER BY 1;

-- Q48: Readmission rate by discharge disposition (top 10)
SELECT rds.description,
       COUNT(*) AS n,
       ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_pct
FROM admissions a
JOIN ref_discharge_disposition rds ON a.discharge_disposition_id = rds.discharge_disposition_id
GROUP BY rds.description HAVING COUNT(*) >= 500
ORDER BY readmit_pct DESC LIMIT 10;

-- Q49: Medication analysis — insulin dosage changes
SELECT dosage_status, COUNT(*) AS n
FROM medications WHERE medication_name = 'insulin'
GROUP BY dosage_status;

-- Q50: Executive summary — all key KPIs in one query
SELECT
    (SELECT COUNT(*) FROM patients)                    AS total_patients,
    (SELECT COUNT(*) FROM admissions)                  AS total_admissions,
    (SELECT ROUND(AVG(time_in_hospital)::numeric, 2) FROM admissions) AS avg_los,
    (SELECT ROUND(100.0 * SUM(CASE WHEN readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2)
     FROM admissions)                                  AS readmission_rate_pct,
    (SELECT COUNT(*) FROM v_high_risk_patients
     WHERE risk_tier IN ('High', 'Critical'))          AS high_risk_patients,
    (SELECT icd_group FROM v_readmission_by_diagnosis
     WHERE diagnosis_rank = 1 ORDER BY admission_count DESC LIMIT 1) AS top_diagnosis;
