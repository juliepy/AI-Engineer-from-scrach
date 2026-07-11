# RELIABILITY.md

Ce fichier définit comment le système prouve qu'il est sain et redémarrable.

## Chemins standard

- Amorçage : `[command]`
- Vérification : `[command]`
- Lancement de l'application ou du service : `[command]`
- Débogage ou inspection de l'exécution : `[command]`

## Signaux d'exécution requis

- journaux structurés pour le démarrage et les flux critiques
- vérifications de santé pour les services clés
- données de trace ou de minutage pour les chemins lents lorsque disponibles
- états d'erreur visibles par l'utilisateur pour les défaillances récupérables

## Parcours de référence

- `[parcours 1]`
- `[parcours 2]`
- `[parcours 3]`

Chaque parcours de référence doit avoir un chemin de vérification répétable et des
signaux d'échec clairs.

## Règles de fiabilité

- Aucune fonctionnalité n'est terminée si le système ne peut pas redémarrer proprement
  ensuite.
- Les défaillances d'exécution doivent être diagnostiquables à partir de signaux locaux
  au dépôt.
- Si un mode de défaillance répété apparaît, ajoutez un benchmark ou un garde-fou pour
  celui-ci.
- Le nettoyage fait partie de la fiabilité, pas d'un souci séparé.
