# Orchestration Airflow

Docker Compose démarre les services. Airflow gère l’ordre, les reprises, les journaux et l’historique des traitements.

```text
verifier_sources
      ↓
tester_transformations
      ↓
charger_entrepot
      ↓
publier_vues_analytiques
```

## Démarrage

```bash
docker compose --profile orchestration build airflow airflow-init
docker compose --profile orchestration up airflow-init
docker compose --profile orchestration up -d airflow
```

Ouvrir `http://localhost:8080`, activer `baac_datawarehouse_pipeline`, puis choisir **Trigger DAG**. Configuration facultative :

```json
{"start_year": 2024, "end_year": 2024}
```

Chaque tâche est retentée une fois après deux minutes. Une tâche aval ne démarre que si la précédente réussit.

Cette installation pédagogique utilise `SequentialExecutor` et SQLite. Une production multi-utilisateur devrait utiliser PostgreSQL pour les métadonnées Airflow et `LocalExecutor` ou `CeleryExecutor`.
