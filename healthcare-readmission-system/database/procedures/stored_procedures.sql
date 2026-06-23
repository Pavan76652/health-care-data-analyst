-- Stored procedures for KPI refresh and analytics
SET search_path TO healthcare, public;

-- -----------------------------------------------------------------------------
-- sp_get_dashboard_kpis — Executive dashboard metrics
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_get_dashboard_kpis()
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE '--- Healthcare Readmission Dashboard KPIs ---';
    PERFORM * FROM v_readmission_summary;
END;
$$;

-- Returns KPIs as a result set (callable from apps)
CREATE OR REPLACE FUNCTION fn_dashboard_kpis()
RETURNS TABLE (
    total_patients              BIGINT,
    total_admissions            BIGINT,
    avg_length_of_stay          NUMERIC,
    readmission_rate_30_day_pct NUMERIC,
    readmissions_within_30_days BIGINT,
    high_utilization_admissions BIGINT
)
LANGUAGE sql STABLE
AS $$
    SELECT * FROM v_readmission_summary;
$$;

-- -----------------------------------------------------------------------------
-- sp_readmission_rate_by_gender
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_readmission_rate_by_gender()
RETURNS TABLE (
    gender              VARCHAR,
    admission_count     BIGINT,
    readmit_30_count    BIGINT,
    readmission_rate_pct NUMERIC
)
LANGUAGE sql STABLE
AS $$
    SELECT
        p.gender,
        COUNT(a.admission_id),
        SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2)
    FROM admissions a
    JOIN patients p ON a.patient_id = p.patient_id
    GROUP BY p.gender
    ORDER BY readmission_rate_pct DESC;
$$;

-- -----------------------------------------------------------------------------
-- sp_readmission_rate_by_age
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_readmission_rate_by_age()
RETURNS TABLE (
    age_bracket         VARCHAR,
    admission_count     BIGINT,
    readmit_30_count    BIGINT,
    readmission_rate_pct NUMERIC
)
LANGUAGE sql STABLE
AS $$
    SELECT
        p.age_bracket,
        COUNT(a.admission_id),
        SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2)
    FROM admissions a
    JOIN patients p ON a.patient_id = p.patient_id
    GROUP BY p.age_bracket
    ORDER BY p.age_midpoint;
$$;

-- -----------------------------------------------------------------------------
-- sp_top_diagnoses_by_readmission
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_top_diagnoses_by_readmission(p_limit INT DEFAULT 10)
RETURNS TABLE (
    icd_group           VARCHAR,
    admission_count     BIGINT,
    readmit_30_count    BIGINT,
    readmission_rate_pct NUMERIC
)
LANGUAGE sql STABLE
AS $$
    SELECT
        d.icd_group,
        COUNT(DISTINCT a.admission_id),
        SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END),
        ROUND(
            100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END)
                / NULLIF(COUNT(DISTINCT a.admission_id), 0),
            2
        )
    FROM diagnosis d
    JOIN admissions a ON d.admission_id = a.admission_id
    WHERE d.diagnosis_rank = 1
      AND d.icd_group <> 'Unknown'
    GROUP BY d.icd_group
    ORDER BY readmission_rate_pct DESC
    LIMIT p_limit;
$$;

-- -----------------------------------------------------------------------------
-- sp_patient_readmission_history
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_patient_readmission_history(p_patient_id BIGINT)
RETURNS TABLE (
    admission_id        BIGINT,
    time_in_hospital    SMALLINT,
    readmitted          VARCHAR,
    readmitted_30_days  BOOLEAN,
    primary_diagnosis   VARCHAR
)
LANGUAGE sql STABLE
AS $$
    SELECT
        a.admission_id,
        a.time_in_hospital,
        a.readmitted,
        a.readmitted_30_days,
        d.icd_group
    FROM admissions a
    LEFT JOIN diagnosis d ON a.admission_id = d.admission_id AND d.diagnosis_rank = 1
    WHERE a.patient_id = p_patient_id
    ORDER BY a.admission_id;
$$;

-- -----------------------------------------------------------------------------
-- sp_refresh_materialized_stats (placeholder for scheduled jobs)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_log_etl_refresh(p_source VARCHAR, p_rows BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'ETL refresh: source=%, rows=%', p_source, p_rows;
END;
$$;

-- -----------------------------------------------------------------------------
-- sp_medication_readmission_analysis
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_insulin_readmission_rate()
RETURNS TABLE (
    on_insulin          VARCHAR,
    admission_count     BIGINT,
    readmission_rate_pct NUMERIC
)
LANGUAGE sql STABLE
AS $$
    SELECT
        a.on_insulin,
        COUNT(*),
        ROUND(100.0 * SUM(CASE WHEN a.readmitted_30_days THEN 1 ELSE 0 END) / COUNT(*), 2)
    FROM admissions a
    GROUP BY a.on_insulin;
$$;
