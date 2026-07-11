# SOP : Boucle de validation Chrome DevTools

Utilisez cette SOP lorsque le travail sur l'interface utilisateur dépend d'interactions
réelles à l'exécution et que les captures d'écran, l'état du DOM et la sortie console
sont plus importants que la simple inspection du code.

## Objectif

Transformer la validation de l'interface utilisateur en une boucle d'interaction
répétable que l'agent peut exécuter jusqu'à ce que le parcours soit propre.

## Boucle principale

1. Sélectionner la page cible ou l'instance de l'application.
2. Effacer le bruit de console obsolète.
3. Capturer l'état AVANT.
4. Déclencher le parcours dans l'interface.
5. Observer les événements d'exécution pendant l'interaction.
6. Capturer l'état APRÈS.
7. Appliquer le correctif et redémarrer l'application si nécessaire.
8. Relancer la validation jusqu'à ce que le parcours soit propre.

## Entrées requises

- une commande de démarrage stable
- un parcours d'interface reproductible
- un moyen de capturer le DOM, la console ou des captures d'écran
- une règle définissant ce qui est considéré comme « propre »

## SOP d'exécution

1. Écrire le parcours cible dans le plan actif.
2. Définir le succès en termes observables : texte présent, bouton activé,
   erreur disparue, console propre, requête réussie.
3. Capturer l'état initial avant l'interaction.
4. Déclencher exactement un seul parcours à la fois.
5. Enregistrer les événements d'exécution, les changements du DOM et la sortie visible.
6. Si le parcours échoue, corriger la couche responsable la plus petite et redémarrer.
7. Relancer le même parcours et comparer les preuves AVANT/APRÈS.

## Critères de propreté

- l'état visible attendu est présent
- les erreurs inattendues sont absentes
- le bruit de console est compris ou effacé
- relancer le même parcours donne le même résultat

## Artefacts du dépôt à mettre à jour

- plan d'exécution actif
- `docs/RELIABILITY.md` si le parcours devient un chemin de référence
- spécification produit si le comportement visible a changé
