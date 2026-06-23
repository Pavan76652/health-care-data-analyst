-- Master initialization script
-- Run: psql -U postgres -d healthcare_readmission -f database/init_database.sql

\echo '=== Creating schema ==='
\i database/schema/01_create_tables.sql

\echo '=== Loading reference data ==='
\i database/seeds/01_reference_inserts.sql

\echo '=== Creating indexes ==='
\i database/indexes/create_indexes.sql

\echo '=== Creating views ==='
\i database/views/analytics_views.sql

\echo '=== Creating stored procedures ==='
\i database/procedures/stored_procedures.sql

\echo '=== Schema ready. Generate CSVs with: python database/scripts/generate_seed_data.py ==='
\echo '=== Then bulk load with: psql -f database/seeds/03_bulk_load.sql ==='
