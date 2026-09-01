CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS audit;

COMMENT ON SCHEMA raw IS 'Copies fidèles des données sources après ingestion.';
COMMENT ON SCHEMA staging IS 'Données nettoyées, normalisées et préparées.';
COMMENT ON SCHEMA dw IS 'Modèle dimensionnel destiné aux usages analytiques.';
COMMENT ON SCHEMA audit IS 'Exécutions ETL, contrôles qualité et rejets.';

