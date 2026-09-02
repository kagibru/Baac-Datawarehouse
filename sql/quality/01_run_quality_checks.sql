-- Contrôles qualité du dernier chargement ETL réussi.
-- Le script est réexécutable : les résultats du run courant sont remplacés.

DELETE FROM audit.quality_result
WHERE run_id = (
    SELECT run_id FROM audit.etl_run
    WHERE status = 'SUCCESS'
    ORDER BY run_id DESC LIMIT 1
);

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value FROM dw.fact_accident
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q001', 'Volume total des accidents 2019-2024', 'ERROR',
       CASE WHEN actual_value = 327628 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 327628, 'Une ligne attendue par accident BAAC.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM (SELECT num_acc FROM dw.fact_accident GROUP BY num_acc HAVING COUNT(*) > 1) duplicates
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q002', 'Absence de Num_Acc dupliqués', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Nombre de clés métier présentes plusieurs fois.'
FROM latest CROSS JOIN result;

WITH expected(millesime_source, expected_count) AS (
    VALUES (2019, 58840), (2020, 47744), (2021, 56518),
           (2022, 55302), (2023, 54822), (2024, 54402)
), actual AS (
    SELECT millesime_source, COUNT(*) AS actual_count
    FROM dw.fact_accident GROUP BY millesime_source
), result AS (
    SELECT COUNT(*) FILTER (WHERE COALESCE(actual_count, 0) <> expected_count)::numeric AS actual_value
    FROM expected LEFT JOIN actual USING (millesime_source)
), latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q003', 'Volumes conformes pour chaque millésime', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Nombre de millésimes dont le volume diffère de la source caractéristiques.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT (
        COUNT(*) FILTER (WHERE d.date_key IS NULL) +
        COUNT(*) FILTER (WHERE h.horaire_key IS NULL) +
        COUNT(*) FILTER (WHERE l.localisation_key IS NULL) +
        COUNT(*) FILTER (WHERE r.route_key IS NULL) +
        COUNT(*) FILTER (WHERE c.circonstance_key IS NULL)
    )::numeric AS actual_value
    FROM dw.fact_accident f
    LEFT JOIN dw.dim_date d ON d.date_key = f.date_key
    LEFT JOIN dw.dim_horaire h ON h.horaire_key = f.horaire_key
    LEFT JOIN dw.dim_localisation l ON l.localisation_key = f.localisation_key
    LEFT JOIN dw.dim_route r ON r.route_key = f.route_key
    LEFT JOIN dw.dim_circonstance c ON c.circonstance_key = f.circonstance_key
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q004', 'Intégrité des clés étrangères', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Somme des références sans membre de dimension correspondant.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE nombre_victimes <> nombre_tues + nombre_blesses_hospitalises + nombre_blesses_legers
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q005', 'Cohérence du nombre de victimes', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Victimes = tués + blessés hospitalisés + blessés légers.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE nombre_usagers < nombre_victimes
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q006', 'Nombre d usagers supérieur ou égal aux victimes', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Une victime est obligatoirement comprise dans les usagers.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE nombre_vehicules < 0 OR nombre_usagers < 0 OR nombre_victimes < 0
       OR nombre_tues < 0 OR nombre_blesses_hospitalises < 0 OR nombre_blesses_legers < 0
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q007', 'Absence de mesures négatives', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Mesures quantitatives principales contrôlées.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE latitude IS NOT NULL AND (latitude < -90 OR latitude > 90)
       OR longitude IS NOT NULL AND (longitude < -180 OR longitude > 180)
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q008', 'Coordonnées géographiques valides', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Latitude [-90,90] et longitude [-180,180].'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident f
    JOIN dw.dim_date d ON d.date_key = f.date_key
    WHERE f.date_key = 0 OR d.annee <> f.millesime_source
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q009', 'Dates cohérentes avec le millésime', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Aucune date inconnue et année calendaire égale au millésime.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE horaire_key = 0 OR localisation_key = 0 OR route_key = 0 OR circonstance_key = 0
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q010', 'Utilisation des membres Non renseigné', 'WARNING',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Accidents rattachés à au moins un membre de dimension inconnu.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE accident_count <> 1 OR nombre_lieux_associes < 1
       OR est_accident_mortel <> (nombre_tues > 0)
       OR est_multi_voies <> (nombre_lieux_associes > 1)
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q011', 'Cohérence des indicateurs d accident', 'ERROR',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Compteur, mortalité et indicateur multi-voies.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE nombre_usagers <> nombre_indemnes + nombre_victimes
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q012', 'Couverture de la gravité des usagers', 'WARNING',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Accidents comportant au moins un code gravité absent ou non reconnu.'
FROM latest CROSS JOIN result;

WITH latest AS (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
), result AS (
    SELECT COUNT(*)::numeric AS actual_value
    FROM dw.fact_accident
    WHERE nombre_usagers <> nombre_conducteurs + nombre_passagers + nombre_pietons
)
INSERT INTO audit.quality_result (run_id, check_code, check_name, severity, status, actual_value, expected_value, details)
SELECT run_id, 'Q013', 'Couverture de la catégorie des usagers', 'WARNING',
       CASE WHEN actual_value = 0 THEN 'PASS' ELSE 'FAIL' END,
       actual_value, 0, 'Accidents comportant au moins un code catégorie absent ou non reconnu.'
FROM latest CROSS JOIN result;

-- Restitution lisible à la fin d'une exécution manuelle.
SELECT check_code, check_name, severity, status, actual_value, expected_value, details
FROM audit.quality_result
WHERE run_id = (
    SELECT run_id FROM audit.etl_run WHERE status = 'SUCCESS' ORDER BY run_id DESC LIMIT 1
)
ORDER BY check_code;
