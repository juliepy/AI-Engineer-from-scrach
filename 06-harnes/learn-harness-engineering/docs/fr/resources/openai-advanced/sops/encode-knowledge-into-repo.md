# SOP : Encoder les connaissances invisibles dans le dépôt

Utilisez cette SOP lorsque du contexte important se trouve encore dans Google Docs,
les fils de discussion, les tickets ou dans la tête des gens.

## Objectif

Rendre les connaissances invisibles pour l'agent découvrables dans le codebase
pour qu'une nouvelle session puisse agir dessus sans s'appuyer sur une conversation antérieure.

## Signaux déclencheurs

- L'agent demande constamment comment fonctionne le système.
- Des humains disent « on a décidé ça sur Slack » ou « suis ce que X a dit la semaine dernière. »
- Les revues font référence à des règles produit ou de sécurité qui ne sont pas écrites dans le dépôt.
- Les nouvelles sessions répètent un travail de découverte qui devrait déjà être établi.

## SOP d'exécution

1. Lister les sources de connaissances invisibles : docs, chats, règles d'équipe implicites,
   décisions verbales.
2. Pour chaque source, se demander : s'agit-il d'architecture, de comportement produit,
   de politique de sécurité, d'attente de fiabilité, de contexte de planification ou de
   matériel de référence ?
3. L'encoder dans l'artefact de dépôt correspondant :
   - architecture -> `ARCHITECTURE.md`
   - comportement produit -> `docs/product-specs/`
   - justification de conception -> `docs/design-docs/`
   - état d'exécution -> `docs/exec-plans/`
   - références externes répétées -> `docs/references/`
   - attentes de qualité ou de fiabilité -> `docs/QUALITY_SCORE.md` ou `docs/RELIABILITY.md`
4. Remplacer les formulations vagues par un langage opérationnellement utile.
5. Supprimer ou déprécier les copies obsolètes pour que le dépôt conserve
   une seule vérité découvrable.

## Règles de bon encodage

- Écrire pour la découvabilité, pas pour l'exhaustivité littéraire.
- Préférer des documents courts avec des noms de fichiers clairs.
- Lier les artefacts connexes entre eux.
- Stocker des règles durables, pas des comptes rendus de réunion.
- Mettre à jour le dépôt dans la même session où la décision est prise.

## Définition du « fini »

- Un nouvel agent peut découvrir la règle concernée sans demander à un humain.
- Le même fait n'est pas dispersé dans plusieurs fichiers contradictoires.
- Le nouvel artefact se trouve à proximité du code ou du flux de travail qu'il régit.
