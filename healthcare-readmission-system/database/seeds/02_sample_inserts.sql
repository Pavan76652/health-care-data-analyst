-- Sample INSERT statements (first 5 records)
SET search_path TO healthcare, public;

INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) VALUES (135, 'Caucasian', 'Female', '[50-60)', 55);
INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) VALUES (378, 'Caucasian', 'Female', '[50-60)', 55);
INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) VALUES (729, 'Caucasian', 'Female', '[80-90)', 85);
INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) VALUES (774, 'Caucasian', 'Female', '[80-90)', 85);
INSERT INTO patients (patient_id, race, gender, age_bracket, age_midpoint) VALUES (927, 'AfricanAmerican', 'Female', '[30-40)', 35);

INSERT INTO admissions (admission_id, patient_id, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_medications, readmitted, readmitted_30_days) VALUES (2278392, 8222157, 6, 25, 1, 1, 1, 'NO', FALSE);
INSERT INTO admissions (admission_id, patient_id, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_medications, readmitted, readmitted_30_days) VALUES (149190, 55629189, 1, 1, 7, 3, 18, '>30', FALSE);
INSERT INTO admissions (admission_id, patient_id, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_medications, readmitted, readmitted_30_days) VALUES (64410, 86047875, 1, 1, 7, 2, 13, 'NO', FALSE);
INSERT INTO admissions (admission_id, patient_id, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_medications, readmitted, readmitted_30_days) VALUES (500364, 82442376, 1, 1, 7, 2, 16, 'NO', FALSE);
INSERT INTO admissions (admission_id, patient_id, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_medications, readmitted, readmitted_30_days) VALUES (16680, 42519267, 1, 1, 7, 1, 8, 'NO', FALSE);
