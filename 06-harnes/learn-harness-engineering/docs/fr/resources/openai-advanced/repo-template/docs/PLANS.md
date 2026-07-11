# PLANS.md

Ce fichier définit la manière dont les plans d'exécution sont créés, mis à jour, complétés
et archivés.

## Quand un plan est nécessaire

Créez un plan d'exécution lorsque le travail :

- s'étend sur plus d'une session
- modifie plus d'un sous-système
- comporte des risques de vérification ou de déploiement non négligeables
- dépend de décisions en cours qui doivent être consignées

## Emplacements des plans

- `docs/exec-plans/active/` : plans pilotant actuellement le travail
- `docs/exec-plans/completed/` : plans terminés conservés pour le contexte futur des agents
- `docs/exec-plans/tech-debt-tracker.md` : travail différé et suivis

## Sections minimales d'un plan

- objectif
- périmètre et hors périmètre
- chemin de vérification
- risques et obstacles
- journal de progression
- décisions en cours

## Règles de fonctionnement

- Un plan actif doit avoir une étape actuelle clairement attribuée.
- Mettez à jour le plan au fil de l'avancement ; ne le traitez pas comme un texte statique.
- Si une décision modifie la direction de l'implémentation, consignez-la dans le plan.
- Déplacez les plans terminés vers `completed/` afin que les agents puissent encore retrouver le contexte antérieur.
