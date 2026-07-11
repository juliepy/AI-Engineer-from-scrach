# FRONTEND.md

Ce fichier définit les attentes stables du frontend pour que les agents n'inventent pas
des motifs d'interface de manière imprévisible.

## Principes d'UI

- Optimisez pour la clarté avant la nouveauté.
- Gardez les flux d'interaction découvrables et redémarrables.
- Préférez un petit nombre de composants réutilisables plutôt que des variantes à usage unique.
- Les vérifications d'accessibilité font partie de la vérification normale, pas du travail
  de finition.

## Garde-fous

- Documentez le système de design ou la bibliothèque de composants dans `docs/references/`.
- Enregistrez les états clés visibles par l'utilisateur : vide, chargement, succès, erreur,
  nouvelle tentative.
- Gardez le texte, le comportement clavier et la hiérarchie visuelle cohérents entre les flux.
- Lorsqu'un bug d'interface est corrigé, ajoutez ou mettez à jour l'étape de validation
  correspondante.

## Attentes de vérification

- Capturez des preuves pour les parcours utilisateur critiques.
- Enregistrez les étapes de validation navigateur ou d'exécution dans le plan pertinent.
- Si les régressions visuelles sont fréquentes, standardisez les vérifications par captures
  d'écran ou contrôles du DOM.
