# Carte des méthodes

Ce tableau fait correspondre les modes d'échec les plus courants des agents de codage
en exécution longue à l'artefact ou à la règle de fonctionnement qui les corrige
généralement en premier.

| Mode d'échec | À quoi cela ressemble en pratique | Correctif principal | Artefact de support |
| --- | --- | --- | --- |
| Confusion au démarrage à froid | Une nouvelle session passe la majeure partie de son temps à redécouvrir la configuration et l'état | Faire du dépôt le système de référence | `claude-progress.md` |
| Dérapage du périmètre | L'agent démarre plusieurs fonctionnalités et n'en termine aucune correctement | Restreindre le périmètre actif | `feature_list.json` |
| Achèvement prématuré | L'agent déclare avoir terminé après des modifications de code mais avant une preuve exécutable | Lier l'achèvement à des preuves | `clean-state-checklist.md` |
| Démarrage fragile | Chaque session réapprend comment démarrer le projet | Standardiser la configuration et la vérification | `init.sh` |
| Passation faible | La session suivante ne peut pas dire ce qui est vérifié, cassé ou à venir | Terminer par une passation explicite | `session-handoff.md` |
| Revue subjective | La qualité de la revue dépend du goût ou de la mémoire | Noter la sortie avec des catégories fixes | `evaluator-rubric.md` |

## Principe de fonctionnement

Ajouter le plus petit artefact qui traite directement le mode d'échec observé.
Éviter de résoudre chaque problème de fiabilité en déversant plus de texte
dans un seul fichier d'instructions global.
