# BAAC Decisionnel

Système d'information décisionnel consacré à l'analyse des accidents corporels de la circulation routière en France entre 2019 et 2024.

## Objectif

Construire une chaîne reproductible couvrant :

```text
Sources BAAC + INSEE
        -> ingestion
        -> contrôles et nettoyage
        -> transformations
        -> Data Warehouse PostgreSQL
        -> requêtes analytiques
        -> tableaux de bord
```

La granularité cible de la table de faits est : **une ligne par accident**.

## Modèle décisionnel retenu

Le Data Warehouse adopte un schéma en étoile composé de cinq dimensions et
d'une table de faits à la granularité d'un accident :

```text
dim_date -----------+
dim_horaire --------+
dim_localisation ---+--> fact_accident
dim_route ----------+
dim_circonstance ---+
```

Les fichiers `usagers`, `vehicules` et `lieux` sont agrégés par `Num_Acc`
avant le chargement. Cela garantit une seule ligne par accident et empêche les
doubles comptages dans les indicateurs.

## Sources

- BAAC : caractéristiques, lieux, véhicules et usagers, millésimes 2019 à 2024.
- INSEE : Code officiel géographique 2024 et populations de référence 2022.

Les données volumineuses ne sont pas versionnées dans Git. Consultez `data/README.md` pour les préparer.

## Technologies

- PostgreSQL 16 : stockage du Data Warehouse.
- Python 3.12 et Pandas : ETL.
- SQL : structures, transformations et requêtes analytiques.
- Metabase Community : restitution reproductible.
- Docker Compose : exécution locale de l'ensemble.

## Structure

```text
baac-datawarehouse/
|-- data/
|   |-- raw/baac/
|   |-- raw/insee/
|   `-- sample/
|-- dashboard/
|-- docker/
|-- docs/
|-- etl/
|-- sql/
|   |-- init/
|   |-- ddl/
|   |-- quality/
|   `-- analytics/
|-- tests/
|-- .env.example
|-- docker-compose.yml
`-- README.md
```

## Démarrage prévu

1. Copier `.env.example` vers `.env` et conserver les valeurs de démonstration localement.
2. Placer les sources dans les dossiers décrits dans `data/README.md`.
3. Démarrer PostgreSQL et Metabase :

```bash
docker compose up -d postgres metabase
```

4. Exécuter l'ETL :

```bash
docker compose run --rm etl
```

Les commandes deviendront fonctionnelles à la fin de l'implémentation de l'ETL et du modèle physique.

## Documentation

- `docs/01_cadrage_metier.md`
- `docs/02_architecture.md`
- `docs/03_modele_dimensionnel.md`
- `docs/04_regles_etl.md`
- `docs/05_controles_qualite.md` (à venir)

## Sécurité

- Aucun secret réel ne doit être commité.
- Le fichier `.env` est ignoré par Git.
- Seul `.env.example` est versionné.
