# AGENTS.md

Ce dépôt est optimisé pour le travail des agents de codage longue durée. Gardez ce fichier
court. Utilisez-le comme couche de routage vers les documents du système de référence,
et non comme un dump géant d'instructions.

## Flux de démarrage

Avant de modifier le code :

1. Confirmez la racine du dépôt avec `pwd`.
2. Lisez `ARCHITECTURE.md` pour la carte actuelle du système et les règles strictes de dépendance.
3. Lisez `docs/QUALITY_SCORE.md` pour voir quels domaines ou couches sont les plus faibles.
4. Lisez `docs/PLANS.md`, puis ouvrez le plan actif sur lequel vous travaillez.
5. Lisez la spécification produit pertinente dans `docs/product-specs/`.
6. Exécutez le chemin standard d'amorçage et de vérification pour ce dépôt.
7. Si la vérification de base échoue, réparez la ligne de base avant d'ajouter du périmètre.

## Carte de routage

- `ARCHITECTURE.md` : carte des domaines, modèle de couches, règles de dépendance
- `docs/design-docs/index.md` : décisions de conception et croyances fondamentales
- `docs/product-specs/index.md` : comportements actuels du produit et critères d'acceptation
- `docs/PLANS.md` : cycle de vie des plans et politique des plans d'exécution
- `docs/QUALITY_SCORE.md` : santé des domaines produit et des couches
- `docs/RELIABILITY.md` : signaux d'exécution, benchmarks et attentes de redémarrage
- `docs/SECURITY.md` : secrets, sandbox, données et règles d'actions externes
- `docs/FRONTEND.md` : contraintes UI, règles du système de design, vérifications d'accessibilité

## Contrat de travail

- Travaillez à partir d'un plan délimité ou d'une tranche de fonctionnalité à la fois.
- Ne marquez pas le travail comme terminé par simple inspection du code ; une preuve
  exécutable est requise.
- Si vous modifiez un comportement, mettez à jour les documents produit, plan ou fiabilité
  correspondants dans la même session.
- Si vous observez des retours de revue répétés, promouvez-les en une règle mécanique,
  un contrôle ou un linter plutôt que de les réexpliquer dans le chat.
- Gardez le contenu généré dans `docs/generated/` et les références sources dans
  `docs/references/`.
- Préférez ajouter de petits documents à jour plutôt que de faire grossir ce fichier.

## Définition de « terminé »

Une modification n'est terminée que lorsque toutes les conditions suivantes sont remplies :

- le comportement cible est implémenté
- la vérification requise a réellement été exécutée
- la preuve est liée depuis le plan ou le document de qualité pertinent
- les documents affectés restent à jour
- le dépôt peut redémarrer proprement depuis le chemin de démarrage standard

## Fin de session

Avant de terminer une session :

1. Mettez à jour le plan d'exécution actif.
2. Mettez à jour `docs/QUALITY_SCORE.md` si un domaine ou une couche a changé de manière significative.
3. Enregistrez la nouvelle dette dans `docs/exec-plans/tech-debt-tracker.md` si vous l'avez différée.
4. Déplacez les plans terminés vers `docs/exec-plans/completed/` si approprié.
5. Laissez le dépôt dans un état redémarrable avec une prochaine action claire.
