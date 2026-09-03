# Tableau de bord Metabase

Le tableau de bord **Sécurité routière BAAC** est connecté aux vues PostgreSQL du schéma `reporting`.

## Pages

1. **Vue d’ensemble** : accidents, victimes, tués, hospitalisés, mortalité, évolution, régions et routes.
2. **Évolution temporelle** : tendances annuelle et mensuelle, jours et heures à risque.
3. **Analyse géographique** : régions, départements, communes et carte.
4. **Routes & circonstances** : route, météo, surface, luminosité et collision.

## Aperçu du rendu local

- [Vue d’ensemble](../docs/visuels%20metabase/01_Tableau%20de%20Bord_Vue%20ensemble.png)
- [Évolution temporelle](../docs/visuels%20metabase/02_Tableau%20de%20Bord_Evolution%20Temporelle.png)
- [Analyse géographique](../docs/visuels%20metabase/03_Tableau%20de%20Bord_Analyse%20G%C3%A9ographique.png)
- [Routes et circonstances](../docs/visuels%20metabase/04_Tableau%20de%20Bord_Routes_et_Circonstances.png)

Ces captures documentent le rendu obtenu localement. Elles permettent de consulter le résultat attendu même si la configuration interne de Metabase n’est pas reconstruite automatiquement.

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
