# Politique de Porte de Réussite

Une fonctionnalité ne peut passer de `passes: false` à `passes: true` que lorsque :

- le flux de travail attendu a été exercé
- la preuve de succès est enregistrée
- aucune erreur bloquante n'est présente dans le chemin testé
- l'implémentation ne laisse pas l'application dans un état cassé ou ambigu
