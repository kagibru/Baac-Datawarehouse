-- ============================================================
-- Vues analytiques temporelles
-- ============================================================


-- 1. Évolution annuelle
CREATE OR REPLACE VIEW reporting.v_evolution_annuelle AS
WITH activite_annuelle AS (
    SELECT
        d.annee,
        SUM(f.accident_count) AS nombre_accidents,
        SUM(f.nombre_vehicules) AS nombre_vehicules,
        SUM(f.nombre_usagers) AS nombre_usagers,
        SUM(f.nombre_victimes) AS nombre_victimes,
        SUM(f.nombre_tues) AS nombre_tues,
        SUM(f.nombre_blesses_hospitalises)
            AS blesses_hospitalises,
        SUM(f.nombre_blesses_legers)
            AS blesses_legers
    FROM dw.fact_accident f
    JOIN dw.dim_date d
        ON d.date_key = f.date_key
    GROUP BY d.annee
)

SELECT
    annee,
    nombre_accidents,
    nombre_vehicules,
    nombre_usagers,
    nombre_victimes,
    nombre_tues,
    blesses_hospitalises,
    blesses_legers,

    ROUND(
        100.0 * nombre_tues
        / NULLIF(nombre_victimes, 0),
        2
    ) AS taux_mortalite_victimes_pct,

    LAG(nombre_accidents) OVER (
        ORDER BY annee
    ) AS accidents_annee_precedente,

    ROUND(
        100.0 * (
            nombre_accidents
            - LAG(nombre_accidents) OVER (ORDER BY annee)
        )
        / NULLIF(
            LAG(nombre_accidents) OVER (ORDER BY annee),
            0
        ),
        2
    ) AS evolution_accidents_pct

FROM activite_annuelle;


-- 2. Évolution mensuelle
CREATE OR REPLACE VIEW reporting.v_evolution_mensuelle AS
SELECT
    d.annee,
    d.mois,
    d.mois_nom,
    d.annee_mois,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_usagers) AS nombre_usagers,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key

GROUP BY
    d.annee,
    d.mois,
    d.mois_nom,
    d.annee_mois;

