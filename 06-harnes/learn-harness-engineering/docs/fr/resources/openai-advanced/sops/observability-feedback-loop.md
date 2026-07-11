# SOP : Boucle de rétroaction d'observabilité

Utilisez cette SOP lorsque le débogage est lent, que les agents affirment leur succès
sans preuve, ou que le comportement à l'exécution est plus difficile à inspecter
que le code lui-même.

## Objectif

Donner à l'agent une boucle de rétroaction locale sur les journaux, métriques,
traces et charges de travail exécutables pour qu'il puisse raisonner à partir
de l'exécution, et non seulement de l'inspection du code.

## Pile minimale

- l'application émet des journaux structurés
- l'application émet des métriques et des traces lorsque c'est possible
- couche locale de distribution ou de collecte
- interfaces de requête pour les journaux, métriques et traces
- charge de travail ou parcours utilisateur répétable à relancer après chaque changement

## SOP d'exécution

1. Définir les parcours d'exécution de référence les plus importants.
2. Ajouter des journaux structurés au démarrage et sur le chemin critique.
3. Ajouter des métriques pour la latence, les compteurs d'échecs ou la profondeur
   de file d'attente lorsque c'est utile.
4. Ajouter des traces ou des marqueurs de temps pour les flux lents ou multi-étapes.
5. Rendre les signaux interrogeables depuis l'environnement de développement local.
6. Donner à l'agent une charge de travail ou un scénario répétable à relancer.
7. Exiger la boucle : interroger -> corréler -> raisonner -> implémenter ->
   redémarrer -> relancer -> vérifier.

## Liste de contrôle de session de débogage

- Qu'est-ce qui a échoué ?
- Quel signal prouve l'échec ?
- Quelle couche est propriétaire de l'échec ?
- Qu'est-ce qui a changé après le correctif ?
- L'application a-t-elle redémarré correctement ?
- La même charge de travail a-t-elle réussi après relance ?

## Définition du « fini »

- L'agent peut expliquer un mode d'échec à partir de preuves d'exécution.
- La même charge de travail peut être relancée après chaque changement.
- Le redémarrage et la relance font partie de la boucle de tâches normale.
- Les signaux de fiabilité sont documentés dans `docs/RELIABILITY.md`.
