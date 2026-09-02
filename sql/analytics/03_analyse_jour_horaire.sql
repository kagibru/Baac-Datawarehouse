-- ============================================================
-- Analyse des jours et des horaires
-- ============================================================


-- 1. Activité par jour de la semaine
CREATE OR REPLACE VIEW reporting.v_jour_semaine AS
SELECT
    d.jour_semaine_iso,
    d.jour_nom,
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

GROUP BY
    d.jour_semaine_iso,
    d.jour_nom,
    d.annee;



-- 1. Activité par période de la journée
CREATE OR REPLACE VIEW reporting.v_periode_journee AS
SELECT
    h.periode_journee,

    CASE h.periode_journee
        WHEN 'Nuit' THEN 1
        WHEN 'Matin' THEN 2
        WHEN 'Après-midi' THEN 3
        WHEN 'Soir' THEN 4
        ELSE 5
    END AS ordre_periode,

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

JOIN dw.dim_horaire h
    ON h.horaire_key = f.horaire_key

JOIN dw.dim_date d
    ON d.date_key = f.date_key

GROUP BY h.periode_journee, d.annee;

-- 3 . Activité par heure
CREATE OR REPLACE VIEW reporting.v_activite_horaire AS
SELECT
    h.heure,
    LPAD(h.heure::text, 2, '0') || 'h'
        AS heure_libelle,
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

JOIN dw.dim_horaire h
    ON h.horaire_key = f.horaire_key

JOIN dw.dim_date d
    ON d.date_key = f.date_key

WHERE h.horaire_key <> 0

GROUP BY h.heure, d.annee;

--4 Matrice jour × heure

CREATE OR REPLACE VIEW reporting.v_heatmap_jour_heure AS
SELECT
    d.jour_semaine_iso,
    d.jour_nom,
    h.heure,
    LPAD(h.heure::text, 2, '0') || 'h'
        AS heure_libelle,
    SUM(f.accident_count) AS nombre_accidents,
    SUM(f.nombre_victimes) AS nombre_victimes,
    SUM(f.nombre_tues) AS nombre_tues,
    d.annee

FROM dw.fact_accident f

JOIN dw.dim_date d
    ON d.date_key = f.date_key

JOIN dw.dim_horaire h
    ON h.horaire_key = f.horaire_key

WHERE h.horaire_key <> 0

GROUP BY
    d.jour_semaine_iso,
    d.jour_nom,
    h.heure,
    d.annee;
