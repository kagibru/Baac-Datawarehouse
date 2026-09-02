CREATE OR REPLACE VIEW reporting.v_kpi_global AS
SELECT
    SUM(accident_count) AS nombre_accidents,
    SUM(nombre_vehicules) AS nombre_vehicules,
    SUM(nombre_usagers) AS nombre_usagers,
    SUM(nombre_victimes) AS nombre_victimes,
    SUM(nombre_tues) AS nombre_tues,
    SUM(nombre_blesses_hospitalises) AS blesses_hospitalises,
    SUM(nombre_blesses_legers) AS blesses_legers,
    SUM(nombre_indemnes) AS nombre_indemnes,
    SUM(
        CASE WHEN est_accident_mortel THEN 1 ELSE 0 END
    ) AS accidents_mortels,

    ROUND(
        100.0 * SUM(nombre_tues)
        / NULLIF(SUM(nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    ROUND(
        100.0 * SUM(
            CASE WHEN est_accident_mortel THEN 1 ELSE 0 END
        )
        / NULLIF(SUM(accident_count), 0),
        2
    ) AS taux_accidents_mortels_pct

FROM dw.fact_accident;

COMMENT ON VIEW reporting.v_kpi_global IS
    'Indicateurs globaux des accidents BAAC.';