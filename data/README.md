# Préparation reproductible des données

Les fichiers volumineux ne sont pas stockés dans Git. Ils sont reconstruits à partir des sources publiques officielles.

## Sources officielles

- BAAC 2005–2024 : <https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024>
- Code officiel géographique 2024 : <https://www.insee.fr/fr/information/7766585>
- Populations de référence 2022 : <https://www.insee.fr/fr/statistiques/8290591>

## 1. Télécharger les fichiers BAAC

Depuis la racine du dépôt :

```bash
python scripts/download_baac.py --start-year 2019 --end-year 2024
```

Le script interroge l’API data.gouv.fr, télécharge les quatre fichiers métier de chaque année et produit `data/raw/baac/manifest.json` avec les URL, tailles et empreintes SHA-256.

Fichiers attendus :

```text
caracteristiques-2019.csv ... caracteristiques-2024.csv
lieux-2019.csv              ... lieux-2024.csv
vehicules-2019.csv          ... vehicules-2024.csv
usagers-2019.csv            ... usagers-2024.csv
```

Le cinquième fichier consolidé éventuellement proposé sur data.gouv.fr n’est pas utilisé par l’ETL.

## 2. Construire le référentiel INSEE

Téléchargement automatique :

```bash
python scripts/prepare_insee_reference.py
```

Si l’INSEE modifie ses URL, télécharger les deux archives depuis les pages officielles puis exécuter :

```bash
python scripts/prepare_insee_reference.py \
  --cog-zip chemin/cog_ensemble_2024_csv.zip \
  --population-zip chemin/populations_reference_2022.zip
```

Le résultat est écrit dans :

```text
data/raw/insee/ref_geographie_2024_population_2022.csv
```

## 3. Vérifier les sources

```bash
python scripts/check_sources.py
```

Le contrôle valide la présence des 24 fichiers BAAC, leur lisibilité, l’identifiant d’accident et le référentiel INSEE.

## 4. Lancer l’ETL

```bash
docker compose run --rm etl
```

## Git et licences

Les CSV, ZIP et manifestes locaux restent ignorés par Git. Les scripts, la documentation et les structures de dossiers sont versionnés. Les données BAAC sont publiées sous Licence Ouverte ; conserver l’attribution au ministère de l’Intérieur/ONISR. Les référentiels INSEE doivent également être cités dans le rapport.
