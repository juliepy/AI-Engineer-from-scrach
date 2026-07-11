# Playbook de l'agent initialiseur

Utilisez ce playbook pour la première session sérieuse dans un dépôt, avant que
le travail incrémental sur les fonctionnalités ne commence.

## Objectif

Créer une surface de fonctionnement stable pour que les sessions ultérieures puissent
implémenter le comportement sans avoir à redériver les commandes de démarrage,
l'état actuel ou les limites des tâches.

## Sorties requises

L'initialiseur doit laisser au moins ces artefacts :

- un fichier d'instructions racine tel que `AGENTS.md` ou `CLAUDE.md`
- une surface de fonctionnalités lisible par machine telle que `feature_list.json`
- un artefact de progression durable tel que `claude-progress.md`
- un assistant de démarrage standard tel que `init.sh`
- un commit initial sûr capturant l'échafaudage de référence

## Liste de contrôle

1. Définir le chemin de démarrage standard.
2. Définir le chemin de vérification standard.
3. Créer le journal de progression et enregistrer l'état de départ.
4. Décomposer le travail en fonctionnalités explicites avec des statuts.
5. Créer le premier commit de référence propre.

## Test de réussite

Une nouvelle session sans contexte de conversation antérieur doit pouvoir répondre :

- ce que fait ce dépôt
- comment le démarrer
- comment le vérifier
- ce qui est inachevé
- quelle est la meilleure prochaine étape
