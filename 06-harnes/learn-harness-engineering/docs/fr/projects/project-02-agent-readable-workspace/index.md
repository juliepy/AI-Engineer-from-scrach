[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> Leçons liées : [Leçon 03. Faire du dépôt votre source de vérité unique](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [Leçon 04. Répartir les instructions entre plusieurs fichiers](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Fichiers modèles : [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/fr/resources/templates/)

# Projet 02. Rendre le projet lisible et reprendre là où vous vous êtes arrêté

## Ce que vous faites

Ajoutez de la "lisibilité" au dépôt pour qu'un nouvel agent comprenne rapidement la structure du projet, connaisse l'avancement actuel et reprenne le travail. Concrètement : implémentez l'import de documents, la vue de détail et la persistance locale, en deux sessions.

Vous l'exécutez deux fois : d'abord sans aide, puis avec `ARCHITECTURE.md`, `PRODUCT.md` et `session-handoff.md` déjà placés dans le dépôt.

## Utiliser le projet fourni

Chemin dans le dépôt : [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Dossier | Contenu | À comparer |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Code de Project 01 avec import, vue détail et persistance encore incomplets. La documentation existe, mais elle est plus légère et il n'y a pas de `session-handoff.md`. | Combien de contexte une deuxième session doit redécouvrir. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | Même tranche produit terminée, avec documentation de reprise sous [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution), plus [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) et [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md). | Si une nouvelle session peut reprendre uniquement depuis l'état du dépôt. |

## Outils

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mécanisme de harness

Workspace lisible par l'agent + fichiers d'état persistants
