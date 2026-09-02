-- ============================================================
-- Vue détaillée destinée à Metabase
-- Granularité : une ligne par accident
-- ============================================================

CREATE OR REPLACE VIEW reporting.v_accident_detail AS
SELECT
    -- Identifiant
    f.num_acc,
    f.accident_count,

    -- Date
    d.full_date AS date_accident,
    d.annee,
    d.trimestre,
    d.mois,
    d.mois_nom,
    d.annee_mois,
    d.semaine_iso,
    d.jour,
    d.jour_semaine_iso,
    d.jour_nom,
    d.est_weekend,

    -- Horaire
    h.heure,
    h.minute,
    h.heure_libelle,
    h.tranche_horaire,
    h.periode_journee,

    -- Localisation
    l.code_commune,
    l.commune,
    l.code_departement,
    l.departement,
    l.code_region,
    l.region,
    l.population_municipale_2022,

    -- Route
    r.categorie_route_code,
    r.categorie_route,
    r.circulation_code,
    r.circulation,
    r.nombre_voies,
    r.voie_reservee,
    r.profil,
    r.trace,
    r.etat_surface,
    r.infrastructure,
    r.situation,
    r.vitesse_maximale,
    r.tranche_vitesse,

    -- Circonstances
    c.luminosite,
    c.type_zone,
    c.intersection,
    c.meteo,
    c.type_collision,

    -- Mesures
    f.nombre_vehicules,
    f.nombre_usagers,
    f.nombre_victimes,
    f.nombre_indemnes,
    f.nombre_tues,
    f.nombre_blesses_hospitalises,
    f.nombre_blesses_legers,
    f.nombre_conducteurs,
    f.nombre_passagers,
    f.nombre_pietons,
    f.nombre_vehicules_legers,
    f.nombre_deux_roues,
    f.nombre_poids_lourds,
    f.nombre_lieux_associes,

    -- Indicateurs
    f.est_accident_mortel,
    f.est_multi_voies,

    -- Informations géographiques détaillées
    f.adresse,
    f.voie_principale,
    f.latitude,
    f.longitude,

    -- Traçabilité
    f.millesime_source

FROM dw.fact_accident f

JOIN dw.dim_date d
    ON d.date_key = f.date_key

JOIN dw.dim_horaire h
    ON h.horaire_key = f.horaire_key

JOIN dw.dim_localisation l
    ON l.localisation_key = f.localisation_key

JOIN dw.dim_route r
    ON r.route_key = f.route_key

JOIN dw.dim_circonstance c
    ON c.circonstance_key = f.circonstance_key;