# AGENTS.md

Ce dépôt est conçu pour le travail d'agents de codage en exécution longue. L'objectif
n'est pas de maximiser la production brute de code. L'objectif est de laisser le dépôt
dans un état où la prochaine session peut continuer sans avoir à deviner.

## Flux de démarrage

Avant d'écrire du code :

1. Confirmer le répertoire de travail avec `pwd`.
2. Lire `claude-progress.md` pour connaître le dernier état vérifié et la prochaine étape.
3. Lire `feature_list.json` et choisir la fonctionnalité inachevée la plus prioritaire.
4. Examiner les commits récents avec `git log --oneline -5`.
5. Exécuter `./init.sh`.
6. Exécuter la vérification de fumée ou de bout en bout requise avant de commencer
   un nouveau travail.

Si la vérification de référence échoue déjà, corriger cela en premier. Ne pas empiler
de nouveau travail sur un état de départ cassé.

## Règles de travail

- Travailler sur une seule fonctionnalité à la fois.
- Ne pas marquer une fonctionnalité comme terminée uniquement parce que du code a été ajouté.
- Garder les modifications dans le périmètre de la fonctionnalité sélectionnée, sauf si
  un obstacle impose un correctif de support restreint.
- Ne pas modifier silencieusement les règles de vérification pendant l'implémentation.
- Préférer les artefacts durables du dépôt aux résumés de conversation.

## Artefacts requis

- `feature_list.json` : source de vérité pour l'état des fonctionnalités
- `claude-progress.md` : journal de session et état vérifié actuel
- `init.sh` : chemin standard de démarrage et de vérification
- `session-handoff.md` : passation compacte optionnelle pour les sessions plus importantes

## Définition du « fini »

Une fonctionnalité est terminée uniquement lorsque toutes les conditions suivantes sont
remplies :

- le comportement cible est implémenté
- la vérification requise a réellement été exécutée
- les preuves sont enregistrées dans `feature_list.json` ou `claude-progress.md`
- le dépôt reste redémarrable depuis le chemin de démarrage standard

## Fin de session

Avant de terminer une session :

1. Mettre à jour `claude-progress.md`.
2. Mettre à jour `feature_list.json`.
3. Enregistrer tout risque ou obstacle non résolu.
4. Valider avec un message descriptif une fois le travail dans un état sûr.
5. Laisser le dépôt suffisamment propre pour que la prochaine session puisse exécuter
   `./init.sh` immédiatement.
