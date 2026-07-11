[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Leçons liées : [Leçon 09. Empêcher les agents de déclarer la victoire trop tôt](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Leçon 10. Seule une exécution de pipeline complet compte comme vraie vérification](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Fichiers modèles : [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/fr/resources/templates/)

# Projet 05. Faire vérifier son propre travail par l'agent

## Ce que vous faites

Implémentez la séparation des rôles : un generator qui implémente, un evaluator qui relit, et éventuellement un planner. Exécutez trois fois pour mesurer l'effet de chaque rôle ajouté.

Choisissez une amélioration substantielle de fonctionnalité, comme une conversation multi-tour, une refonte du panneau de citations ou un filtrage de documents, et gardez-la identique dans toutes les exécutions.

## Utiliser le projet fourni

Chemin dans le dépôt : [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Dossier | Contenu | À comparer |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Application basée sur Project 04 avant l'ajout de l'historique conversationnel. | Point de départ pour relancer les trois variantes. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Un agent planifie, implémente et s'auto-évalue. | Score et défauts dans [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Générateur + évaluateur avec preuve de révision. | Score et notes de révision dans [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner + générateur + évaluateur avec sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) et preuves de score plus élevé dans [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## Outils

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mécanisme de harness

Auto-vérification + Q&A fondé sur des sources + finalisation basée sur des preuves
