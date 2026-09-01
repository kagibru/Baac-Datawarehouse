# Préparation des données

## BAAC

Placer les 24 fichiers 2019 à 2024 dans `data/raw/baac/` :

```text
caracteristiques-2019.csv
caracteristiques-2020.csv
carcteristiques-2021.csv
carcteristiques-2022.csv
caract-2023.csv
caract-2024.csv
lieux-2019.csv ... lieux-2024.csv
vehicules-2019.csv ... vehicules-2024.csv
usagers-2019.csv ... usagers-2024.csv
```

L'ETL reconnaîtra les trois variantes du nom du fichier Caractéristiques et normalisera `Accident_Id` en `Num_Acc` pour 2022.

## INSEE

Le référentiel préparé attendu est :

```text
data/raw/insee/ref_geographie_2024_population_2022.csv
```

Il regroupe le Code officiel géographique 2024, les arrondissements municipaux, les collectivités d'outre-mer, les communes historiques et les populations de référence 2022.

## Git

Les CSV ne sont pas versionnés. La procédure de téléchargement et les contrôles d'intégrité seront documentés afin de garantir la reproductibilité.

