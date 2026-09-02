# Contrôles qualité

## Objectif

Les contrôles vérifient que le Data Warehouse respecte sa granularité, ses
volumes sources et ses règles métier. Ils sont enregistrés dans
`audit.quality_result` et rattachés au dernier chargement réussi.

## Exécution manuelle dans Docker

Depuis la racine du projet :

```powershell
docker compose exec -T postgres psql `
  -U baac_user `
  -d baac_dw `
  -f /opt/baac/sql/quality/01_run_quality_checks.sql
```

Le script est réexécutable : les résultats du même `run_id` sont remplacés.

## Consultation synthétique

```sql
SELECT check_code, check_name, severity, status,
       actual_value, expected_value
FROM audit.quality_result
WHERE run_id = (SELECT MAX(run_id) FROM audit.quality_result)
ORDER BY check_code;
```

## Interprétation

- `ERROR / FAIL` : règle structurelle ou métier bloquante ;
- `WARNING / FAIL` : donnée source incomplète à documenter, sans suppression ;
- `PASS` : valeur observée conforme à la valeur attendue.

Les contrôles couvrent les volumes, les doublons, les clés étrangères, les
victimes, les usagers, les mesures négatives, les coordonnées, les dates et les
membres inconnus.

## Automatisation

Lors d'un nouveau chargement, `etl.run_pipeline` exécute automatiquement le
script après l'opération d'UPSERT. Il reste possible de le relancer seul avec
la commande Docker ci-dessus.

