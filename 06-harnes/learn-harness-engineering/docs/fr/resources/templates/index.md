# Guide des modèles

Ces modèles sont prêts à être copiés dans votre propre projet. Chacun remplit un
rôle spécifique dans le flux de travail de l'agent. Modifiez le contenu pour
l'adapter aux commandes, chemins, noms de fonctionnalités et étapes de vérification
de votre projet.

## Pour commencer

Copiez d'abord ces quatre fichiers à la racine de votre projet :

1. `AGENTS.md` ou `CLAUDE.md`
2. `init.sh`
3. `claude-progress.md`
4. `feature_list.json`

Ajoutez les fichiers restants au fur et à mesure que votre projet grandit.

---

## AGENTS.md

Le fichier d'instructions racine. C'est la première chose que l'agent lit lorsqu'il
démarre une session. Il définit les règles de fonctionnement : quoi faire avant
d'écrire du code, comment travailler et comment conclure.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Remplacez les étapes du flux de démarrage par vos chemins et commandes réels
- Ajustez les règles de travail pour correspondre aux conventions de votre équipe
- Conservez la section de définition du « fini » — c'est la partie la plus importante

**Ce qu'il fait pour l'agent :**

- Lui dit de lire la progression et l'état des fonctionnalités avant de commencer le travail
- Le force à travailler sur une seule fonctionnalité à la fois
- Exige des preuves avant de marquer quoi que ce soit comme terminé
- Définit à quoi ressemble une fin de session propre

Utilisez `AGENTS.md` pour Codex ou d'autres agents. Utilisez `CLAUDE.md` si vous
travaillez avec Claude Code — la structure est la même, simplement formatée pour le
style d'instructions de Claude.

## init.sh

Le script de démarrage. Exécute l'installation des dépendances, la vérification
et affiche la commande de lancement — le tout en une seule fois.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Modifiez ces trois variables en haut :
  - `INSTALL_CMD` — votre commande d'installation des dépendances (par ex. `npm install`, `pip install -r requirements.txt`)
  - `VERIFY_CMD` — votre commande de vérification de base (par ex. `npm test`, `pytest`)
  - `START_CMD` — votre commande de lancement du serveur de développement (par ex. `npm run dev`)
- Rendez-le exécutable : `chmod +x init.sh`

**Ce qu'il fait :**

1. Affiche le répertoire courant (pour confirmer qu'il s'exécute au bon endroit)
2. Installe les dépendances
3. Exécute la commande de vérification
4. Affiche la commande de lancement (ou l'exécute si `RUN_START_COMMAND=1` est défini)

Si la vérification échoue, l'agent doit s'arrêter et corriger la ligne de base avant
de faire quoi que ce soit d'autre.

## claude-progress.md

Le journal de progression. Chaque session écrit dans ce fichier, et chaque nouvelle
session le lit en premier.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Remplissez la section « État vérifié actuel » avec les informations de votre projet
- Après chaque session, mettez à jour l'enregistrement de session

**Signification de chaque champ :**

- **État vérifié actuel** — l'unique source de vérité sur l'état du projet
  - `Racine du dépôt` — où se trouve le projet
  - `Chemin de démarrage standard` — la commande pour lancer le projet
  - `Chemin de vérification standard` — la commande pour exécuter les tests
  - `Fonctionnalité inachevée la plus prioritaire` — sur quoi la prochaine session devrait travailler
  - `Obstacle actuel` — tout ce qui est bloqué
- **Enregistrement de session** — une entrée par session
  - `Objectif` — ce que vous aviez prévu de faire
  - `Terminé` — ce qui a réellement été accompli
  - `Vérification exécutée` — quels tests ont été lancés
  - `Preuves enregistrées` — quelles preuves ont été capturées
  - `Commits` — ce qui a été validé
  - `Risques connus` — ce qui pourrait être cassé
  - `Meilleure prochaine action` — où la prochaine session devrait commencer

## feature_list.json

Le suivi des fonctionnalités. Une liste lisible par machine de chaque fonctionnalité
que l'agent doit implémenter, avec son statut, ses étapes de vérification et ses preuves.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Remplacez les exemples de fonctionnalités par les vôtres
- Chaque fonctionnalité nécessite :
  - `id` — un identifiant court unique
  - `priority` — entier, plus bas = plus prioritaire
  - `area` — quelle partie de l'application (par ex. « chat », « import », « search »)
  - `title` — description courte
  - `user_visible_behavior` — ce que l'utilisateur doit voir quand ça fonctionne
  - `status` — parmi `not_started`, `in_progress`, `blocked`, `passing`
  - `verification` — instructions étape par étape pour confirmer le bon fonctionnement
  - `evidence` — preuves enregistrées que la vérification a réussi (remplies par l'agent)
  - `notes` — tout contexte supplémentaire

**Règles de statut :**

- `not_started` — n'a pas été touché
- `in_progress` — la fonctionnalité en cours de travail (une seule à la fois)
- `blocked` — ne peut pas progresser en raison d'un problème documenté
- `passing` — la vérification a réussi et les preuves sont enregistrées

L'agent ne doit avoir qu'une seule fonctionnalité en `in_progress` à tout moment.

## session-handoff.md

Une note de passation compacte entre les sessions. Utilisez-la lorsqu'une session se
termine et que vous souhaitez que la prochaine reprenne rapidement.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Remplissez-la à la fin de chaque session (ou demandez à l'agent de la remplir)

**Ce que chaque section couvre :**

- **Actuellement vérifié** — ce qui est confirmé fonctionnel et quelle vérification a été exécutée
- **Changements cette session** — quel code ou infrastructure a changé
- **Encore cassé ou non vérifié** — problèmes connus et zones à risque
- **Meilleure prochaine action** — ce que la prochaine session doit faire, et ce qu'il ne faut pas toucher
- **Commandes** — démarrage, vérification et commandes de débogage pour référence rapide

Ce fichier est optionnel pour les petites sessions. Il devient important lorsque les
sessions sont longues ou lorsque le projet a plusieurs zones actives.

## clean-state-checklist.md

Une liste de contrôle à passer avant de terminer chaque session. S'assure que le dépôt
est dans un bon état pour que la prochaine session puisse démarrer proprement.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Passez-la en revue avant de fermer une session
- L'agent doit également vérifier ces éléments dans le cadre de sa routine de fin de session

**Ce qu'elle vérifie :**

- Le démarrage standard fonctionne toujours
- La vérification standard s'exécute toujours
- Le journal de progression est mis à jour
- La liste des fonctionnalités reflète l'état réel (pas de fausses entrées `passing`)
- Aucun travail à moitié terminé laissé non enregistré
- La prochaine session peut continuer sans corrections manuelles

## evaluator-rubric.md

Une fiche d'évaluation pour la qualité des résultats de l'agent. Utilisez-la après
une session ou à des jalons du projet pour évaluer si le travail atteint le niveau requis.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Après une session (ou un ensemble de sessions), notez le travail de l'agent sur six dimensions
- Chaque dimension est notée de 0 à 2

**Les six dimensions :**

1. **Correction** — l'implémentation correspond-elle au comportement cible ?
2. **Vérification** — les vérifications requises ont-elles réellement été exécutées, avec des preuves ?
3. **Discipline de périmètre** — l'agent est-il resté dans la fonctionnalité sélectionnée ?
4. **Fiabilité** — le résultat survit-il à un redémarrage ou à une relance ?
5. **Maintenabilité** — le code et la documentation sont-ils suffisamment clairs pour la prochaine session ?
6. **Préparation à la passation** — une nouvelle session peut-elle continuer en utilisant uniquement les artefacts du dépôt ?

**Options de verdict :**

- Accepter — atteint le niveau requis
- Réviser — nécessite des correctifs avant acceptation
- Bloquer — problèmes fondamentaux à résoudre en premier

**Important : l'évaluateur nécessite un réglage.** Tel quel, les agents sont de mauvais
juges d'eux-mêmes — ils identifient des problèmes puis se convainquent d'approuver.
Vous devrez itérer :

1. Exécutez l'évaluateur sur un sprint terminé.
2. Comparez ses scores avec votre propre jugement humain.
3. Lorsqu'ils divergent, rendez la grille plus spécifique sur les critères de réussite/échec.
4. Réexécutez et vérifiez l'alignement.
5. Répétez jusqu'à ce que l'évaluateur corresponde systématiquement à la revue humaine.

Prévoyez 3 à 5 cycles de réglage. Enregistrez chaque changement pour suivre ce qui a
amélioré l'alignement.

## quality-document.md

Un instantané qualité qui note chaque domaine produit et couche architecturale de votre
projet. Suit la santé du codebase au fil du temps, pas seulement les résultats de
sessions individuelles.

**Comment l'utiliser :**

- Copiez à la racine de votre projet
- Avant de démarrer une session : lisez-le pour comprendre où le codebase est le plus faible
- Après une session : mettez à jour les notes en fonction de ce qui a changé
- Au fil du temps : comparez les instantanés pour voir quels changements de harnais ont
  réellement amélioré la santé du codebase

**Ce qu'il évalue :**

- **Domaines produit** (par ex., import de documents, flux Q&R, indexation) : chaque domaine
  reçoit une note (A-D) selon l'état de vérification, la lisibilité agent, la stabilité des
  tests et les lacunes principales
- **Couches architecturales** (par ex., main process, preload, renderer, services) : chaque
  couche reçoit une note pour l'application des limites et la lisibilité agent

**Pourquoi c'est important :**

La grille d'évaluation note les résultats individuels de l'agent. Le document qualité note
le codebase lui-même. Ils répondent à des questions différentes :

- Grille d'évaluation : « L'agent a-t-il fait du bon travail cette session ? »
- Document qualité : « Le projet devient-il plus fort ou plus faible au fil du temps ? »

**Quand mettre à jour :**

- Après chaque session significative
- Avant les comparaisons de benchmarks
- Après les passes de nettoyage ou de simplification
- Lors de l'intégration d'un nouvel agent ou modèle au projet

**Lien avec la simplification du harnais :**

Le document qualité soutient également la simplification du harnais. Chaque composant de
harnais encode une hypothèse sur ce que le modèle ne peut pas faire. À mesure que les
modèles s'améliorent, ces hypothèses deviennent obsolètes. Pour vérifier si un composant
est toujours nécessaire :

1. Prenez un instantané du document qualité.
2. Retirez un composant de harnais.
3. Exécutez la suite de tâches de benchmark.
4. Prenez un autre instantané.
5. Comparez — si les notes n'ont pas baissé, le composant était superflu. Si elles ont baissé,
   restaurez-le.
