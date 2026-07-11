# Flux de démarrage de l'agent de codage

Utilisez ceci au début de chaque session une fois l'initialisation terminée.

## Modèle de démarrage fixe

1. Exécuter `pwd` et confirmer la racine du dépôt.
2. Lire `claude-progress.md`.
3. Lire `feature_list.json`.
4. Examiner les commits récents avec `git log --oneline -5`.
5. Exécuter `./init.sh`.
6. Exécuter un parcours de test de fumée ou de bout en bout de référence.
7. Si la référence est cassée, corriger cela en premier.
8. Sélectionner la fonctionnalité inachevée la plus prioritaire.
9. Travailler uniquement sur cette fonctionnalité jusqu'à ce qu'elle soit
   vérifiée ou explicitement bloquée.

## Pourquoi cet ordre est important

- `pwd` évite un travail accidentel dans le mauvais répertoire.
- Les fichiers de progression et de fonctionnalités restaurent l'état durable
  avant que de nouvelles modifications ne commencent.
- Les commits récents expliquent ce qui a changé le plus récemment.
- `init.sh` standardise le démarrage au lieu de s'appuyer sur la mémoire.
- La vérification de référence intercepte les états de départ cassés avant
  que le nouveau travail ne les cache.

## Miroir de fin de session

La même session devrait se terminer par :

1. l'enregistrement de la progression
2. la mise à jour de l'état des fonctionnalités
3. la rédaction d'une passation si nécessaire
4. la validation du travail sûr
5. le maintien d'un chemin de redémarrage propre
