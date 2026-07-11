# CLAUDE.md

Vous travaillez dans un dépôt conçu pour un travail d'implémentation en exécution longue.
Priorisez l'achèvement fiable, la continuité entre les sessions et la vérification
explicite plutôt que la vitesse.

## Boucle de fonctionnement

Au début de chaque session :

1. Exécuter `pwd` et confirmer que vous êtes à la racine du dépôt attendu.
2. Lire `claude-progress.md`.
3. Lire `feature_list.json`.
4. Examiner les commits récents avec `git log --oneline -5`.
5. Exécuter `./init.sh`.
6. Vérifier si le parcours de fumée ou de bout en bout de référence est déjà cassé.

Ensuite, sélectionner exactement une fonctionnalité inachevée et travailler uniquement
sur cette fonctionnalité jusqu'à ce que vous la vérifiiez ou que vous documentiez
pourquoi elle est bloquée.

## Règles

- Une seule fonctionnalité active à la fois.
- Ne pas déclarer l'achèvement sans preuve exécutable.
- Ne pas réécrire la liste des fonctionnalités pour masquer le travail inachevé.
- Ne pas supprimer ou affaiblir les tests uniquement pour faire paraître la tâche terminée.
- Utiliser les artefacts du dépôt comme système de référence.

## Fichiers requis

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- `session-handoff.md` lorsqu'une passation compacte est utile

## Porte d'achèvement

Une fonctionnalité ne peut passer à `passing` qu'après que la vérification requise
a réussi et que le résultat est enregistré.

## Avant de vous arrêter

1. Mettre à jour le journal de progression.
2. Mettre à jour l'état des fonctionnalités.
3. Enregistrer ce qui est encore cassé ou non vérifié.
4. Valider une fois que le dépôt est sûr à reprendre.
5. Laisser un chemin de redémarrage propre pour la prochaine session.
