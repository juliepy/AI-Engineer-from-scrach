# Skills

Ce dossier contient les skills d'agents IA livrés avec ce cours. Les skills sont des modèles de prompt autonomes que des agents de codage IA, comme Claude Code, Codex, Cursor ou Windsurf, peuvent charger pour effectuer des tâches spécialisées.

## harness-creator

Un skill de harness engineering de niveau production pour agents de codage IA. Il vous aide à créer, évaluer et améliorer les cinq sous-systèmes centraux d'un harness : instructions, état, vérification, scope et cycle de vie de session.

### Ce qu'il fait

- **Créer des harnesses depuis zéro** — AGENTS.md, listes de fonctionnalités, workflows de vérification
- **Améliorer des harnesses existants** — évaluation des cinq sous-systèmes avec améliorations priorisées
- **Concevoir la continuité de session** — persistance mémoire, suivi de progression, procédures de handoff
- **Appliquer des patterns de production** — mémoire, context engineering, sécurité des outils, coordination multi-agent

### Démarrage rapide

Les fichiers du skill se trouvent dans le dépôt sous [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Pour l'utiliser avec Claude Code, copiez le dossier `harness-creator/` dans le chemin de skills de votre projet, ou pointez votre agent vers le fichier SKILL.md.

### Patterns de référence

Le skill inclut 7 documents de référence ciblés :

| Pattern | Quand l'utiliser |
|---------|------------------|
| Memory Persistence | L'agent oublie entre les sessions |
| Skill Runtime | Packager des workflows réutilisables en skills |
| Context Engineering | Gestion du budget de contexte, chargement JIT |
| Tool Registry | Sécurité des outils, contrôle de concurrence |
| Multi-Agent Coordination | Parallélisme, workflows de spécialisation |
| Lifecycle & Bootstrap | Hooks, tâches en arrière-plan, initialisation |
| Gotchas | 15 modes de défaillance non évidents avec correctifs |

### Modèles

Le skill fournit des modèles prêts à l'emploi :

- `agents.md` — scaffold AGENTS.md avec règles de travail
- `feature-list.json` — JSON Schema et exemple de liste de fonctionnalités
- `init.sh` — script d'initialisation standard
- `progress.md` — modèle de journal de progression de session
- `session-handoff.md` — modèle de handoff de session

### Scripts

Le skill inclut aussi des scripts Node.js purs pour le scaffold, la validation, les rapports HTML d'évaluation et les benchmarks structurels.

### Comment ce skill a été construit

`harness-creator` a été développé avec la méthodologie **skill-creator**, le méta-skill officiel d'Anthropic pour créer, tester et itérer sur des skills d'agents. skill-creator fournit un workflow structuré brouillon → test → évaluation → itération, avec runners d'évaluation, graders et visualiseur de benchmark.

- **Source de skill-creator** : [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Documentation des skills Claude Code** : [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
