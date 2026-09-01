# Règles ETL

## Exécution

Le pipeline est lancé depuis la racine du projet :

```powershell
py -m etl.run_pipeline --dry-run
```

Le mode `--dry-run` exécute l'extraction et toutes les transformations sans
écrire dans PostgreSQL. Pour limiter le test à 2024 :

```powershell
py -m etl.run_pipeline --start-year 2024 --end-year 2024 --dry-run
```

Une fois PostgreSQL disponible et les variables `.env` configurées :

```powershell
py -m etl.run_pipeline
```

Avec Docker :

```powershell
docker compose up -d postgres
docker compose run --rm etl
```

## Extraction

- lecture des CSV avec séparateur `;` et colonnes en texte ;
- détection des encodages UTF-8 et Windows-1252 ;
- reconnaissance des variantes `caracteristiques`, `carcteristiques` et `caract` ;
- harmonisation de `Accident_Id` en `num_acc` ;
- ajout du millésime, du fichier et du numéro de ligne source.

## Transformations

- suppression des espaces ordinaires et insécables dans les identifiants ;
- conversion des décimales françaises à virgule ;
- construction des clés date `AAAAMMJJ` et minute de la journée ;
- traduction des codes BAAC en libellés métier ;
- création d'empreintes SHA-256 pour les dimensions Route et Circonstance ;
- agrégation des usagers et véhicules par accident ;
- choix déterministe de la voie principale ;
- rattachement des communes au référentiel INSEE.

## Chargement

Le chargement utilise des opérations `UPSERT`. Une nouvelle exécution met à
jour les accidents déjà présents et ajoute les nouveaux, sans dupliquer
`num_acc`. Les volumes de chaque fichier et de la table de faits sont inscrits
dans le schéma `audit`.

