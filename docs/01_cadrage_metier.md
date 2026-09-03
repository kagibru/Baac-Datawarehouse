# Cadrage métier

## Contexte

Une agence française chargée de la sécurité routière souhaite centraliser les données d'accidents corporels pour identifier les zones, périodes, infrastructures et circonstances prioritaires. Les donnnées proviennent d'une source de données libres disponible à l'adresse

## Problématique

Comment centraliser, nettoyer et historiser les données d'accidents afin d'identifier les périodes, territoires, infrastructures et circonstances associés aux niveaux d'accidentalité et de gravité les plus élevés? Dans cet exercice, nous avons décider de ne pas inclure l'anaylyse liées aux passagers et aux véhicules mais nous recupérerons directement les informations liées à ces paramètres dans notre de faits.

## Source de Données
- https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024
Ici nous avons téléharggé uniquement les données de 2019 à 2024 soit 06 années qui contiennent principalement 04 Tables:
   * CARACTERISTIQUES
   * LIEUX
   * VÉHICULES
   * USAGERS
   cf. fichier Dictionnaire_donnees_BAAC_2005-2024.xlsx

- https://www.insee.fr/fr/information/7766585
  Code officiel géographique au 1er janvier 2024
  Cette table nous permet de réconcilier les codes géographiques avec les libelles pour l'analyse géographique

- https://www.insee.fr/fr/statistiques/8290591
  Téléchargement du fichier d'ensemble des populations en 2022
  Fichier de récemment, qui nous permettra de faire les analyse de taux d'accidents par rapport à la densité de la population

## Périmètre

- France métropolitaine et territoires couverts par BAAC.
- Millésimes 2019 à 2024.
- Processus métier : survenue d'un accident corporel de la circulation.
- Granularité cible : une ligne de fait par accident.

## Utilisateurs

- Direction de la sécurité routière.
- Analystes.
- Responsables territoriaux.
- Gestionnaires d'infrastructures.
- Responsables de la prévention.

## Décisions

- Prioriser les territoires et périodes à risque.
- Identifier les conditions associées aux accidents graves.
- Orienter les campagnes de prévention.
- Étudier les infrastructures et catégories de routes.
- Suivre l'évolution annuelle de l'accidentalité.

## Indicateurs initiaux

1. Nombre d'accidents.
2. Nombre de victimes.
3. Nombre de personnes tuées.
4. Nombre de blessés.
5. Taux d'accidents mortels.
6. Nombre moyen de victimes par accident.
7. Nombre moyen de véhicules par accident.
8. Accidents pour 100 000 habitants.
9. Variation annuelle des accidents.
10. Part des accidents de nuit.
