# Validation et recette

| Domaine | Contrôle | Résultat attendu |
|---|---|---|
| Sources | quatre fichiers métier BAAC par année | fichiers présents et lisibles |
| Grain | unicité de `num_acc` | aucun doublon |
| Modèle | clés étrangères | aucune clé orpheline hors membre inconnu |
| Mesures | victimes | tués + hospitalisés + blessés légers |
| Volumétrie | faits | égale au nombre d’accidents caractéristiques |
| Reporting | vues SQL | toutes interrogeables |
| Dashboard | filtre Année | cartes compatibles actualisées |

## Commandes

```bash
docker compose config --quiet
docker compose run --rm --entrypoint python etl -m pytest -q tests
docker compose run --rm etl --start-year 2024 --end-year 2024 --dry-run
```

## Requêtes

```sql
SELECT count(*) = count(DISTINCT num_acc) AS grain_valide FROM dw.fact_accident;

SELECT count(*) AS mesures_incoherentes
FROM dw.fact_accident
WHERE nombre_victimes <> nombre_tues + nombre_blesses_hospitalises + nombre_blesses_legers;

SELECT table_name FROM information_schema.views
WHERE table_schema = 'reporting' ORDER BY table_name;
```

## Recette Metabase

Ouvrir les quatre onglets, appliquer 2019 puis 2024, vérifier chaque carte, comparer un total à une requête SQL et capturer les écrans définitifs.
