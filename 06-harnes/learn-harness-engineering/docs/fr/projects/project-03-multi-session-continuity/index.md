[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Leçons liées : [Leçon 05. Garder le contexte vivant entre les sessions](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Leçon 06. Initialiser avant chaque session d'agent](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Fichiers modèles : [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/fr/resources/templates/)

# Projet 03. Garder l'agent au travail après les redémarrages de session

## Ce que vous faites

Ajoutez un contrôle de scope et des portes de vérification à l'agent. Implémentez le découpage de documents, l'extraction de métadonnées, l'affichage de progression d'indexation et un flux Q&A avec citations. Utilisez `feature_list.json` pour suivre l'état des fonctionnalités : une fonctionnalité à la fois, sans marquer `pass` sans preuve de vérification.

Vous l'exécutez deux fois : d'abord sans contraintes, puis avec application stricte.

## Utiliser le projet fourni

Chemin dans le dépôt : [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Dossier | Contenu | À comparer |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Code de Project 02 avec indexation et Q&A avec citations encore incomplets. Il contient un premier [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json), mais pas les artefacts finaux de reprise. | Si l'agent dérive entre plusieurs fonctions ou perd l'état après redémarrage. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Chunking, métadonnées, état d'indexation et Q&A avec citations terminés, plus [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Si chaque fonction a une preuve concrète avant d'être marquée comme réussie. |

## Outils

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mécanisme de harness

Journal de progression + handoff de session + continuité multi-session
