# Calibration des prompts

Les instructions racines doivent définir le cadre de fonctionnement, pas chaque
mouvement possible.

## Garder dans le fichier racine

- l'objectif et le périmètre du dépôt
- le chemin de démarrage
- le chemin de vérification
- les contraintes non négociables
- les artefacts d'état requis
- les règles de fin de session

## Sortir du fichier racine

- les cas limites historiques longs
- les détails d'implémentation spécifiques à un sujet
- les notes d'architecture locale qui doivent se trouver près du code
- les exemples qui ne s'appliquent qu'à un seul sous-système

## Règle de travail

Le fichier racine doit aider une nouvelle session à s'orienter rapidement.
Si le fichier devient une poubelle pour chaque échec passé, diviser les détails
en documents plus petits et y faire un lien à la place.
