# Exemple : Transformer un Retour de Review en Règle

Commentaire de review répété :

> N'utilisez pas les utilitaires du système de fichiers depuis le renderer. Utilisez le pont preload.

Règle de harness promue :

- ajouter une règle lint ou d'import empêchant l'utilisation de `fs` dans le code du renderer
- ajouter un texte de remédiation expliquant la frontière du preload
