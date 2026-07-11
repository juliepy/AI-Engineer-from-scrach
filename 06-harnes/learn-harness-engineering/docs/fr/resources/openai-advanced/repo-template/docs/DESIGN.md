# DESIGN.md

Ce fichier est le point d'entrée de la conception. Gardez-le bref et utilisez-le pour
router vers les fichiers plus détaillés sous `docs/design-docs/`.

## Objectif

Enregistrer les décisions de conception produit et système durables qui doivent survivre
au-delà d'une seule conversation, sprint ou mémoire de relecteur.

## Lisez ceci quand

- vous avez besoin de la philosophie de conception actuelle
- vous êtes sur le point d'introduire un nouveau motif
- vous devez savoir quelles décisions de conception sont tranchées versus encore ouvertes

## Documents de conception canoniques

- `docs/design-docs/index.md` : index des documents acceptés, proposés et dépréciés
- `docs/design-docs/core-beliefs.md` : croyances agent-first à l'échelle du projet

## Règles de conception

- Gardez les documents de conception petits et à jour.
- Préférez un document par domaine de décision.
- Liez les documents de conception depuis les plans et spécifications quand un changement en dépend.
- Si une règle de conception devient critique opérationnellement, promouvez-la en un contrôle
  automatisé ou mettez à jour `ARCHITECTURE.md`.
