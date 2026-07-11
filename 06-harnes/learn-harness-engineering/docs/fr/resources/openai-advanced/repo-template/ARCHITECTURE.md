# ARCHITECTURE.md

Ce fichier est la carte de niveau supérieur du système. Il doit rester concis et
renvoyer vers des documents plus détaillés si nécessaire.

## Forme du système

- Produit : `[replace with product name]`
- Flux utilisateur principal : `[replace with main workflow]`
- Surfaces d'exécution : `[desktop / web / cli / services / workers]`
- Source de vérité pour le comportement produit : `docs/product-specs/`

## Carte des domaines

| Domaine | Objectif | Points d'entrée principaux | Spécification associée |
|---------|----------|---------------------------|----------------------|
| `[domain-a]` | `[what it owns]` | `[modules / routes / commands]` | `[spec path]` |
| `[domain-b]` | `[what it owns]` | `[modules / routes / commands]` | `[spec path]` |

## Modèle de couches

Utilisez un modèle directionnel fixe pour que les agents n'inventent pas une architecture
ad hoc :

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Les préoccupations transversales doivent entrer par des frontières explicites de
fournisseur ou d'adaptateur plutôt que d'atteindre directement à travers les couches.

## Règles strictes de dépendance

- Les couches inférieures ne doivent pas dépendre des couches supérieures.
- L'UI ne doit pas contourner les contrats d'exécution ou de service.
- L'accès aux données doit passer par des dépôts ou des adaptateurs équivalents.
- Les utilitaires partagés doivent rester génériques et ne doivent pas accumuler
  de logique métier.
- Les nouvelles dépendances doivent être justifiées dans le plan ou le document
  de conception correspondant.

## Interfaces transversales

| Préoccupation | Frontière approuvée | Notes |
|--------------|--------------------| -----|
| Journalisation et traçage | `[provider / utility path]` | `[structured only, no ad hoc console use]` |
| Authentification | `[provider path]` | `[token/session rules]` |
| APIs externes | `[client or provider path]` | `[rate limit / retry guidance]` |
| Feature flags | `[flag boundary]` | `[ownership]` |

## Points chauds actuels

- `[zone la plus difficile à modifier en toute sécurité pour les agents]`
- `[zone avec des limites faibles ou des tests fragiles]`

## Liste de contrôle des modifications

Lorsque vous modifiez du code pertinent pour l'architecture :

1. Mettez à jour ce fichier si la carte des domaines ou les frontières autorisées
   ont changé.
2. Mettez à jour le document de conception associé dans `docs/design-docs/` si le
   raisonnement a changé.
3. Ajoutez ou mettez à jour un contrôle exécutable si la règle doit être appliquée
   mécaniquement.
