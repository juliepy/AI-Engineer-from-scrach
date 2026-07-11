# Pack Avancé OpenAI

Ce dossier empaquette la structure de dépôt plus opiniâtre décrite dans
l'article d'OpenAI "Harness engineering: leveraging Codex in an agent-first world"
en fichiers de démarrage prêts à copier.

Utilisez ce pack lorsque le harness minimal ne suffit plus et que votre dépôt
a maintenant besoin de :

- un `AGENTS.md` court de style routeur
- des docs durables de système d'enregistrement dans le dépôt
- des plans d'exécution actifs et terminés
- des fichiers de politique explicites pour produit, fiabilité, sécurité et frontend
- un scoring qualité par domaine produit et couche architecturale
- des dossiers de matériel de référence adapté aux modèles
- des procédures opérationnelles standard pour l'architecture, la capture de connaissances et la validation d'exécution

## Mise en Page de Démarrage Incluse

Le pack de démarrage dans [`repo-template/`](./repo-template/index.md) reflète
la structure suivante :

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Comment l'Adopter

1. Commencez avec le pack minimal si votre dépôt est encore petit.
2. Copiez les fichiers dans [`repo-template/`](./repo-template/index.md) dans
   votre propre dépôt lorsque vous avez besoin d'une structure plus forte.
3. Gardez `AGENTS.md` court. Traitez-le comme un routeur vers les docs plus profonds, pas comme une encyclopédie.
4. Mettez à jour les docs de qualité, fiabilité et plans dans le cadre du travail normal, pas comme un jour de nettoyage séparé.
5. Gardez les artefacts générés et les références externes explicites pour que les agents puissent les trouver sans dépendre de l'historique de chat.

## Bibliothèque de SOPs

Le dossier [`sops/`](./sops/index.md) transforme les diagrammes de l'article en
procédures opérationnelles étape par étape :

- configuration d'architecture de domaine en couches
- encodage de connaissances inédites dans le dépôt
- stack d'observabilité locale et flux de travail de boucle de retour
- boucle de validation Chrome DevTools pour le travail UI

## Principes de Conception

- Point d'entrée court, docs plus profonds liés
- Dépôt comme système d'enregistrement
- Les vérifications mécaniques优于 les règles mémorisées
- Les plans et l'historique qualité vivent à côté du code
- Le nettoyage et la simplification sont des responsabilités de premier plan

Ce pack est intentionnellement opiné, mais doit être adapté à votre projet plutôt que copié aveuglément.
