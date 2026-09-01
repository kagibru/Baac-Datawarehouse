\set ON_ERROR_STOP on

\ir /opt/baac/sql/ddl/01_create_dimensions.sql
\ir /opt/baac/sql/ddl/02_create_fact_accident.sql
\ir /opt/baac/sql/ddl/03_create_audit_tables.sql
\ir /opt/baac/sql/ddl/04_seed_unknown_members.sql
