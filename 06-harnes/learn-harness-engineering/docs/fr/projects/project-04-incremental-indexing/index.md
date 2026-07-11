[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Leçons liées : [Leçon 07. Définir des limites de tâche claires pour les agents](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Leçon 08. Utiliser les listes de fonctionnalités pour contraindre ce que fait l'agent](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Fichiers modèles : [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/fr/resources/templates/)

# Projet 04. Utiliser le feedback runtime pour corriger le comportement de l'agent

## Ce que vous faites

Ajoutez de l'observabilité runtime, comme les logs de démarrage, les logs d'import/indexation et les états d'erreur, ainsi que des contraintes d'architecture pour éviter les violations entre couches. Introduisez un bug runtime que l'agent devra corriger.

Vous l'exécutez deux fois : d'abord sans logs ni contraintes, puis avec les bons outils et règles.

## Utiliser le projet fourni

Chemin dans le dépôt : [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Dossier | Contenu | À comparer |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Code de Project 03 avec diagnostics faibles. Le défaut d'indexation intégré peut casser le chunking des gros fichiers, et il n'y a pas de script de contrôle d'architecture. | Le temps nécessaire pour trouver la cause sans signaux runtime. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Logger structuré, documentation/script de frontières d'architecture, logique de chunking corrigée et [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Si les logs et contrôles rendent la correction plus rapide et moins invasive. |

Fichiers clés : [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Outils

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mécanisme de harness

Feedback runtime + contrôle du scope + indexation incrémentale
