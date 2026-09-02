-- ============================================================
-- Analyse géographique
-- ============================================================
--1- Vue régionale
CREATE OR REPLACE VIEW reporting.v_analyse_region AS
WITH accidents_region AS (
    SELECT
        d.annee,
        l.code_region,
        MAX(l.region) AS region,
        SUM(f.accident_count) AS nombre_accidents,
        SUM(f.nombre_usagers) AS nombre_usagers,
        SUM(f.nombre_victimes) AS nombre_victimes,
        SUM(f.nombre_tues) AS nombre_tues,
        SUM(
            CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
        ) AS accidents_mortels
    FROM dw.fact_accident f
    JOIN dw.dim_date d
        ON d.date_key = f.date_key
    JOIN dw.dim_localisation l
        ON l.localisation_key = f.localisation_key
    WHERE l.localisation_key <> 0
      AND l.code_region IS NOT NULL
    GROUP BY d.annee, l.code_region
),

population_region AS (
    SELECT
        code_region,
        SUM(population_municipale_2022) AS population
    FROM dw.dim_localisation
    WHERE localisation_key <> 0
      AND type_commune = 'COM'
      AND code_region IS NOT NULL
    GROUP BY code_region
)

SELECT
    a.code_region,
    a.region,
    a.nombre_accidents,
    a.nombre_usagers,
    a.nombre_victimes,
    a.nombre_tues,
    a.accidents_mortels,
    p.population,

    ROUND(
        100000.0 * a.nombre_accidents
        / NULLIF(p.population, 0),
        2
    ) AS accidents_pour_100000_habitants,

    ROUND(
        100000.0 * a.nombre_tues
        / NULLIF(p.population, 0),
        2
    ) AS tues_pour_100000_habitants,

    ROUND(
        100.0 * a.nombre_tues
        / NULLIF(a.nombre_victimes, 0),
        2
    ) AS taux_mortalite_victimes_pct,

    a.annee

FROM accidents_region a
LEFT JOIN population_region p
    ON p.code_region = a.code_region;


--2- Vue départementale
CREATE OR REPLACE VIEW reporting.v_analyse_departement AS
WITH accidents_departement AS (
    SELECT
        d.annee,
        l.code_departement,
        MAX(l.departement) AS departement,
        MAX(l.code_region) AS code_region,
        MAX(l.region) AS region,
        SUM(f.accident_count) AS nombre_accidents,
        SUM(f.nombre_usagers) AS nombre_usagers,
        SUM(f.nombre_victimes) AS nombre_victimes,
        SUM(f.nombre_tues) AS nombre_tues,
        SUM(
            CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
        ) AS accidents_mortels
    FROM dw.fact_accident f
    JOIN dw.dim_date d
        ON d.date_key = f.date_key
    JOIN dw.dim_localisation l
        ON l.localisation_key = f.localisation_key
    WHERE l.localisation_key <> 0
      AND l.code_departement <> 'N/C'
    GROUP BY d.annee, l.code_departement
),

population_departement AS (
    SELECT
        code_departement,
        SUM(population_municipale_2022) AS population
    FROM dw.dim_localisation
    WHERE localisation_key <> 0
      AND type_commune = 'COM'
      AND code_departement <> 'N/C'
    GROUP BY code_departement
)

SELECT
    a.code_departement,
    a.departement,
    a.code_region,
    a.region,
    a.nombre_accidents,
    a.nombre_usagers,
    a.nombre_victimes,
    a.nombre_tues,
    a.accidents_mortels,
    p.population,

    ROUND(
        100000.0 * a.nombre_accidents
        / NULLIF(p.population, 0),
        2
    ) AS accidents_pour_100000_habitants,

    ROUND(
        100000.0 * a.nombre_tues
        / NULLIF(p.population, 0),
        2
    ) AS tues_pour_100000_habitants,

    ROUND(
        100.0 * a.nombre_tues
        / NULLIF(a.nombre_victimes, 0),
        2
    ) AS taux_mortalite_victimes_pct,

    a.annee

FROM accidents_departement a
LEFT JOIN population_departement p
    ON p.code_departement = a.code_departement;

--3- Vue communale
CREATE OR REPLACE VIEW reporting.v_analyse_commune AS
SELECT
    l.code_commune,
    l.commune,
    l.code_departement,
    l.departement,
    l.code_region,
    l.region,
    l.population_municipale_2022 AS population,

    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_usagers) AS nombre_usagers,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,
    SUM(
        CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
    ) AS accidents_mortels,

    ROUND(
        100000.0 * SUM(f.accident_count)
        / NULLIF(l.population_municipale_2022, 0),
        2
    ) AS accidents_pour_100000_habitants,

    ROUND(
        100000.0 * SUM(f.nombre_tues)
        / NULLIF(l.population_municipale_2022, 0),
        2
    ) AS tues_pour_100000_habitants,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    CASE
        WHEN l.population_municipale_2022 >= 10000
             AND SUM(f.accident_count) >= 10
        THEN true
        ELSE false
    END AS eligible_comparaison_taux,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_localisation l
    ON l.localisation_key = f.localisation_key

JOIN dw.dim_date d
    ON d.date_key = f.date_key

WHERE l.localisation_key <> 0

GROUP BY
    d.annee,
    l.code_commune,
    l.commune,
    l.code_departement,
    l.departement,
    l.code_region,
    l.region,
    l.population_municipale_2022;


--4- Vue des points géographiques des accidents
CREATE OR REPLACE VIEW reporting.v_carte_accidents AS
SELECT
    f.num_acc,
    d.full_date AS date_accident,
    d.annee,
    l.code_commune,
    l.commune,
    l.departement,
    l.region,
    f.latitude,
    f.longitude,
    f.nombre_usagers,
    f.nombre_victimes,
    f.nombre_tues,
    f.est_accident_mortel

FROM dw.fact_accident f

JOIN dw.dim_date d
    ON d.date_key = f.date_key

JOIN dw.dim_localisation l
    ON l.localisation_key = f.localisation_key

WHERE f.latitude IS NOT NULL
  AND f.longitude IS NOT NULL;
