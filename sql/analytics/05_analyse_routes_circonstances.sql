-- ============================================================
-- Analyse des routes et des circonstances
-- ============================================================


-- 1. Catégories de route
CREATE OR REPLACE VIEW reporting.v_categorie_route AS
SELECT
    r.categorie_route_code,
    r.categorie_route,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_vehicules) AS nombre_vehicules,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,
    SUM(
        CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
    ) AS accidents_mortels,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    ROUND(
        100.0 * SUM(
            CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
        )
        / NULLIF(SUM(f.accident_count), 0),
        2
    ) AS taux_accidents_mortels_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_route r
    ON r.route_key = f.route_key

GROUP BY
    d.annee,
    r.categorie_route_code,
    r.categorie_route;


--2. Tranches de vitesse autorisée
    CREATE OR REPLACE VIEW reporting.v_tranche_vitesse AS
SELECT
    r.tranche_vitesse,

    CASE r.tranche_vitesse
        WHEN '0-30' THEN 1
        WHEN '31-50' THEN 2
        WHEN '51-70' THEN 3
        WHEN '71-90' THEN 4
        WHEN '91-110' THEN 5
        WHEN '>110' THEN 6
        ELSE 7
    END AS ordre_tranche,

    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_route r
    ON r.route_key = f.route_key

GROUP BY d.annee, r.tranche_vitesse;


--3- État de la surface
CREATE OR REPLACE VIEW reporting.v_etat_surface AS
SELECT
    r.surface_code,
    r.etat_surface,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_route r
    ON r.route_key = f.route_key

GROUP BY
    d.annee,
    r.surface_code,
    r.etat_surface;


--4. Conditions météorologiques
CREATE OR REPLACE VIEW reporting.v_meteo AS
SELECT
    c.meteo_code,
    c.meteo,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_circonstance c
    ON c.circonstance_key = f.circonstance_key

GROUP BY
    d.annee,
    c.meteo_code,
    c.meteo;



--5. Luminosité
CREATE OR REPLACE VIEW reporting.v_luminosite AS
SELECT
    c.luminosite_code,
    c.luminosite,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_circonstance c
    ON c.circonstance_key = f.circonstance_key

GROUP BY
    d.annee,
    c.luminosite_code,
    c.luminosite;


--6. Types de collision
CREATE OR REPLACE VIEW reporting.v_type_collision AS
SELECT
    c.collision_code,
    c.type_collision,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,
    SUM(
        CASE WHEN f.est_accident_mortel THEN 1 ELSE 0 END
    ) AS accidents_mortels,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f
JOIN dw.dim_date d
    ON d.date_key = f.date_key
JOIN dw.dim_circonstance c
    ON c.circonstance_key = f.circonstance_key

GROUP BY
    d.annee,
    c.collision_code,
    c.type_collision;


--7. Croisement météo et surface
CREATE OR REPLACE VIEW reporting.v_meteo_surface AS
SELECT
    c.meteo,
    r.etat_surface,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,

    ROUND(
        100.0 * SUM(f.nombre_tues)
        / NULLIF(SUM(f.nombre_victimes), 0),
        2
    ) AS taux_mortalite_victimes_pct,

    d.annee

FROM dw.fact_accident f

JOIN dw.dim_date d
    ON d.date_key = f.date_key

JOIN dw.dim_circonstance c
    ON c.circonstance_key = f.circonstance_key

JOIN dw.dim_route r
    ON r.route_key = f.route_key

GROUP BY
    d.annee,
    c.meteo,
    r.etat_surface;
