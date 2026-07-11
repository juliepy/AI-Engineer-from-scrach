# Exemple de Composants du Harness

Pour un agent de programmation travaillant dans un dépôt local :

- Modèle :
  le LLM lui-même

- Harness :
  - prompt système
  - AGENTS.md
  - outil bash
  - outils de lecture/écriture de fichiers
  - accès git
  - système de fichiers local
  - scripts de démarrage
  - commandes de test
  - hooks d'arrêt
  - vérifications lint
  - boucle d'évaluation (evaluator loop)

Si vous modifiez l'une des pièces du harness ci-dessus, vous modifiez l'agent effectif.
