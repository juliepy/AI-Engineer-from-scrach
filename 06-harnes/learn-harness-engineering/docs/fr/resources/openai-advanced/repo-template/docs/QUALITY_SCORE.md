# QUALITY_SCORE.md

Ce document permet de suivre si le dépôt s'améliore ou se dégrade au fil du temps.

## Échelle de notation

- `A` : vérifié, lisible, stable, limites appliquées
- `B` : fonctionnel avec des lacunes mineures
- `C` : partiellement fonctionnel, confusion ou instabilité notable
- `D` : cassé, non sûr ou structurellement peu clair

## Domaines produit

| Domaine | Note | Vérification | Lisibilité agent | Stabilité des tests | Lacunes principales | Dernière mise à jour |
|---------|------|-------------|-----------------|--------------------|--------------------|---------------------|
| `[domain-a]` | - | - | - | - | - | - |
| `[domain-b]` | - | - | - | - | - | - |
| `[domain-c]` | - | - | - | - | - | - |

## Couches architecturales

| Couche | Note | Application des limites | Lisibilité agent | Lacunes principales | Dernière mise à jour |
|--------|------|------------------------|-----------------|--------------------|---------------------|
| Types | - | - | - | - | - |
| Services | - | - | - | - | - |
| Runtime | - | - | - | - | - |
| UI | - | - | - | - | - |

| Date | Variante de harnais | Taux de complétion | Tentatives | Défauts avant revue | Notes |
|------|---------------------|--------------------|------------|--------------------|-------|
| YYYY-MM-DD | `[baseline / improved / simplified]` | - | - | - | - |

## Journal de simplification

| Date | Composant retiré | Résultat | Décision |
|------|-----------------|----------|----------|
| YYYY-MM-DD | `[component]` | `[degraded / unchanged]` | `[restore / keep removed]` |
