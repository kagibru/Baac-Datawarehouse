# BAAC décisionnel

Entrepôt de données consacré à l’analyse des accidents corporels de la circulation routière en France de 2019 à 2024.

## Chaîne décisionnelle

```text
CSV BAAC + référentiels INSEE
            ↓
ETL Python / Pandas
            ↓
PostgreSQL — schéma en étoile
            ↓
Vues SQL du schéma reporting
            ↓
Tableau de bord Metabase
```

Airflow peut orchestrer le traitement. Docker Compose gère les conteneurs ; Airflow gère l’ordre, les reprises et l’historique des tâches.

## Modèle

La table `dw.fact_accident` contient une ligne par accident. Elle est reliée à cinq dimensions : `dim_date`, `dim_horaire`, `dim_localisation`, `dim_route` et `dim_circonstance`.

Les sources `usagers`, `vehicules` et `lieux` sont agrégées par `Num_Acc` avant le chargement afin d’éviter les doubles comptages.

## Démarrage rapide

1. Copier `.env.example` vers `.env` et adapter les mots de passe et ports.
2. Télécharger et préparer les sources :

```bash
python scripts/download_baac.py --start-year 2019 --end-year 2024
python scripts/prepare_insee_reference.py
python scripts/check_sources.py
```

Les URL officielles et la procédure alternative hors ligne sont détaillées dans [data/README.md](data/README.md).
3. Démarrer PostgreSQL et Metabase :

```bash
docker compose up -d postgres metabase
```

4. Exécuter les tests :

```bash
docker compose run --rm --entrypoint python etl -m pytest -q tests
```

5. Exécuter directement l’ETL :

```bash
docker compose run --rm etl
```

6. Publier ou actualiser les vues analytiques :

```bash
docker exec baac-postgres sh -lc 'for f in /opt/baac/sql/analytics/[0-9][0-9]_*.sql; do psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$f"; done'
```

Metabase est ensuite disponible sur `http://localhost:3000`.

## Orchestration Airflow

```bash
docker compose --profile orchestration up airflow-init
docker compose --profile orchestration up -d airflow
```

Ouvrir `http://localhost:8080`, puis déclencher le DAG `baac_datawarehouse_pipeline`. Une plage d’années peut être fournie au déclenchement :

```json
{"start_year": 2019, "end_year": 2024}
```

## Tableau de bord

Le tableau de bord Metabase comporte quatre onglets : vue d’ensemble, évolution temporelle, analyse géographique et routes/circonstances. Voir [dashboard/README.md](dashboard/README.md).

## Documentation

- [Cadrage métier](docs/01_cadrage_metier.md)
- [Architecture](docs/02_architecture.md)
- [Modèle dimensionnel](docs/03_modele_dimensionnel.md)
- [Règles ETL](docs/04_regles_etl.md)
- [Contrôles qualité](docs/05_controles_qualite.md)
- [Guide d’exploitation](docs/06_guide_exploitation.md)
- [Orchestration Airflow](docs/07_orchestration_airflow.md)
- [Validation et recette](docs/08_validation_recette.md)
- [Guide de soutenance](docs/09_guide_soutenance.md)

## Sécurité et versionnement

- `.env` et les données volumineuses ne doivent pas être versionnés ;
- `.env.example` ne contient que des valeurs de démonstration ;
- changer les mots de passe avant tout déploiement partagé ;
- aucun commit Git n’est créé automatiquement par l’assistant.
