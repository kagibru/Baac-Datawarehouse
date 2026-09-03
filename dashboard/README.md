# Tableau de bord Metabase

Le tableau de bord **Sécurité routière BAAC** est connecté aux vues PostgreSQL du schéma `reporting`.

## Pages

1. **Vue d’ensemble** : accidents, victimes, tués, hospitalisés, mortalité, évolution, régions et routes.
2. **Évolution temporelle** : tendances annuelle et mensuelle, jours et heures à risque.
3. **Analyse géographique** : régions, départements, communes et carte.
4. **Routes & circonstances** : route, météo, surface, luminosité et collision.

## Palette

- bleu principal : `#227FD2` ;
- turquoise : `#69C8C8` ;
- orange : `#ED8535` ;
- rouge d’alerte : `#E75454`.

## Filtre global

Le filtre **Année** doit être relié aux champs `annee` des vues compatibles. Après une modification SQL :

1. ouvrir **Admin > Databases > BAAC Data Warehouse** ;
2. lancer **Sync database schema** ;
3. lancer **Re-scan field values** si nécessaire ;
4. vérifier les correspondances du filtre dans l’éditeur du dashboard.

La configuration Metabase est persistée par Docker. Les requêtes SQL sources sont versionnées dans `sql/analytics`.
