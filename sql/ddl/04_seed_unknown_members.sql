INSERT INTO dw.dim_date (
    date_key, full_date, annee, trimestre, mois, mois_nom,
    annee_mois, semaine_iso, jour, jour_semaine_iso, jour_nom, est_weekend
)
VALUES (
    0, DATE '1900-01-01', 1900, 1, 1, 'Non renseigné',
    '1900-01', 1, 1, 1, 'Non renseigné', false
)
ON CONFLICT (date_key) DO NOTHING;

INSERT INTO dw.dim_horaire (
    horaire_key, heure, minute, heure_libelle, tranche_horaire, periode_journee
)
VALUES (0, NULL, NULL, 'N/C  ', 'Non renseignée', 'Non renseignée')
ON CONFLICT (horaire_key) DO NOTHING;

INSERT INTO dw.dim_localisation (
    localisation_key, code_commune, type_commune, code_commune_parente,
    commune, code_departement, departement, code_region, region
)
VALUES (
    0, 'N/C', 'UNKNOWN', NULL,
    'Non renseignée', 'N/C', 'Non renseigné', NULL, 'Non renseignée'
)
ON CONFLICT (localisation_key) DO NOTHING;

INSERT INTO dw.dim_route (
    route_key, route_profile_code, categorie_route, circulation,
    voie_reservee, profil, trace, etat_surface, infrastructure,
    situation, tranche_vitesse
)
VALUES (
    0, repeat('0', 64), 'Non renseignée', 'Non renseignée',
    'Non renseignée', 'Non renseigné', 'Non renseigné', 'Non renseigné',
    'Non renseignée', 'Non renseignée', 'Non renseignée'
)
ON CONFLICT (route_key) DO NOTHING;

INSERT INTO dw.dim_circonstance (
    circonstance_key, circonstance_profile_code, luminosite,
    type_zone, intersection, meteo, type_collision
)
VALUES (
    0, repeat('0', 64), 'Non renseignée',
    'Non renseigné', 'Non renseignée', 'Non renseignée', 'Non renseigné'
)
ON CONFLICT (circonstance_key) DO NOTHING;

