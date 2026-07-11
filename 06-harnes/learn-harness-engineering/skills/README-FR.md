<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

Ce dossier contient des skills réutilisables pour agents IA dans le projet Learn Harness Engineering. Chaque skill est un modèle de prompt autonome pouvant être chargé par des agents de codage comme Claude Code, Codex, Cursor ou Windsurf.

## Skills disponibles

### harness-creator

Skill de harness engineering de niveau production pour agents de codage IA. Elle aide à créer, évaluer et améliorer les fichiers de harness d'agent, notamment AGENTS.md, les listes de fonctionnalités, les workflows de vérification et les mécanismes de continuité de session.

- **7 modèles de référence** : Memory Persistence, Skill Runtime, Context Engineering, Tool Registry, Multi-Agent Coordination, Lifecycle & Bootstrap, Gotchas
- **Templates** : AGENTS.md/CLAUDE.md, feature-list.json, init.sh, progress.md, session-handoff.md
- **Scripts** : scaffold, validation, rapport HTML et benchmark structurel
- **10 cas de test eval intégrés**

Voir la documentation complète : [harness-creator/README.md](harness-creator/README.md).

## Création de harness-creator

`harness-creator` a été développé avec la méthodologie **skill-creator**, le meta-skill officiel d'Anthropic pour créer, tester et itérer des skills d'agents avec un flux draft → test → evaluate → iterate.

## Fonctionnement des skills

Chaque skill suit une structure standard :

1. **SKILL.md** — Point d'entrée avec YAML frontmatter et instructions Markdown pour l'agent.
2. **references/** — Documentation supplémentaire chargée au besoin.
3. **templates/** — Templates de départ que la skill peut générer.

Les skills utilisent le progressive disclosure : l'agent voit d'abord seulement le nom et la description, puis charge SKILL.md au déclenchement, et lit les ressources incluses uniquement si nécessaire.

## Sécurité

Les fichiers de ce dossier ont été audités :

- Aucun backdoor, URL cachée ou payload encodé
- Aucune exfiltration de données ni identifiants codés en dur
- Aucune vulnérabilité de command injection
- Les scripts utilisent uniquement les modules intégrés de Node.js
- Le `init.sh` généré exécute les commandes de vérification détectées du projet

## Licence

MIT
