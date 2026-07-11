# SOP : Architecture en couches par domaine

Utilisez cette SOP lorsque l'agent enfreint constamment les limites, duplique
la logique entre les couches, ou produit du code qui devient difficile à réviser
après quelques sessions.

## Objectif

Rendre les limites de domaine suffisamment explicites pour que les agents puissent
avancer rapidement sans dégrader silencieusement la structure.

## Modèle cible

Au sein d'un domaine métier, privilégiez ce flux directionnel :

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Les préoccupations transversales doivent entrer par des fournisseurs ou adaptateurs
explicites. Les utilitaires partagés restent en dehors du domaine et ne doivent pas
accumuler de logique métier.

## Liste de contrôle de configuration

- Définir les domaines actuels dans `ARCHITECTURE.md`.
- Écrire les directions de dépendance autorisées dans `ARCHITECTURE.md`.
- Enregistrer les interfaces transversales telles que l'authentification,
  la télémétrie et les API externes.
- Ajouter une note courte pour la violation de limite la plus difficile actuellement.
- Décider ce qui doit être appliqué mécaniquement par lint, tests ou scripts.

## SOP d'exécution

1. Cartographier le codebase en domaines avant de toucher au style d'implémentation.
2. Pour chaque domaine, identifier la séquence de couches autorisée.
3. Identifier toutes les préoccupations transversales et les router via des fournisseurs
   ou adaptateurs.
4. Déplacer la logique partagée ambiguë soit dans le domaine propriétaire,
   soit dans des utilitaires véritablement génériques.
5. Documenter les règles dans `ARCHITECTURE.md`.
6. Ajouter un garde-fou exécutable pour la violation au coût le plus élevé.
7. Mettre à jour la notation de qualité après le changement.

## Définition du « fini »

- Un nouvel agent peut dire quelle couche est propriétaire d'un changement.
- Le code de l'interface n'accède plus directement au dépôt ou aux effets de bord externes.
- Les préoccupations transversales ont des points d'entrée nommés.
- Au moins une limite importante est appliquée mécaniquement.

## Artefacts du dépôt à mettre à jour

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/` lorsque la justification a changé
- `docs/PLANS.md` ou le plan d'exécution actif
