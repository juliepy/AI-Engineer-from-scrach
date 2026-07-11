# SOP OpenAI avancées

Ces SOP traduisent les modèles de fonctionnement de l'article en playbooks
d'exécution concrets que vous pouvez suivre ou adapter.

## SOP incluses

- [`layered-domain-architecture.md`](./layered-domain-architecture.md) :
  établir des couches explicites et des limites transversales
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md) :
  déplacer les connaissances invisibles depuis les chats, docs et mémoires
  vers des fichiers locaux au dépôt
- [`observability-feedback-loop.md`](./observability-feedback-loop.md) :
  donner aux agents des journaux, métriques, traces et une boucle de débogage répétable
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md) :
  utiliser l'automatisation de navigateur et des captures pour valider le comportement
  de l'interface utilisateur jusqu'à ce qu'il soit propre

## Comment les utiliser

1. Choisissez la SOP qui correspond à votre goulot d'étranglement actuel.
2. Utilisez la liste de contrôle pour mettre en place les artefacts ou outils manquants.
3. Encodez les règles résultantes dans les docs de votre copie de `repo-template/`.
4. Convertissez les commentaires de revue répétés en vérifications, scripts ou garde-fous.

Ces SOP ne sont pas destinées à être suivies aveuglément. Elles ont pour but de rendre
le harnais plus lisible, applicable et répétable.
