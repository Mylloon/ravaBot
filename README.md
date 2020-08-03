# ravaBot
Bot discord de l'ancienne team des ravaG.


# Infos

La majorité du bot a été codé par moi-même, la musique et l'nsfw ont majoritairement été copié d'internet et revues, je ne me souviens pas d'où cela vient, désolé.

Le bot tournait sur Docker.

Il requiert ffmpeg (pour la musique) et tout le requirements.txt.


# Ce qu'il sait faire

Il a une commande HELP mais voici un résumé de ce qu'il sait faire :

Partie musique :
- connect [id du channel] = Se connecte au salon vocal.
- play <musique> = Recherche une chanson sur Youtube et l'ajoute à la file d'attente.
- pause = Mets en pause de la chanson en cours de lecture.
- resume = Reprends la chanson en pause.
- skip = Passe la chanson.
- queue = Affiche la file d'attente des chansons à venir.
- now_playing = Affiche des informations sur la chanson en cours de lecture.
- volume <valeur>", value=f"Modifiez le volume de <@{ravaBot.id}> (entre 1 et 100).
- disconnect = Arrête la chanson en cours de lecture et quitte le salon vocal.
- lyrics [song] = Affiche les paroles d'une chanson.
Partie XP :
- xp leaderboard = Affiche le top 5 du serveur.
- xp info = Affiche les infos relatives à l'xp.
- xp clear = Supprime l'XP d'un utilisateur.
- xp backup = Envoie une backup en .json des levels des utilisateurs.
- xp give = Permet d'ajouter (ou de retirer si valeur négative) de l'xp à un utilisateur.
Partie divers :
- help [page=1/music/xp] = Affiche le menu d'aide des commandes.
- avatar [user] = Affiche ton avatar ou celui que tu mentionnes.
- kiss = Fait un bisou à un inconnu.
- deglingue = Tu déglingues un inconnu (ou pas).
- suggestion <message de suggestion> = Pour proposé une fonctionnalité.
- ppc <pierre/papier/ciseaux>", value=f"Un simple Chifumi contre <@{ravaBot.id}>.
- ping = Pong!
- iq = Calcule ton IQ.
- chatclear = Clear le canal de discussion.
- eteindre", value=f"Éteint <@{ravaBot.id}>.
- 8ball <question> = Répond a ta question.
- trueid <id> = Renvois à l'utilisateur correspondant.
- calc <calcul> = Calcule une expression.
- mrs = Affiche les messages récemment supprimés.
- reload", value=f"Redémarre <@{ravaBot.id}>.
- ir = Active ou désactive la réponse automatique.
- jvousnik = J'VOUS NIQUE !
- plusoumoins = Un plus ou moins entre 1 et 100.
- vidage = Supprime touts tes messages (uniquement dans le salon <#634059175004995587>).
- delchat <nombre> = Supprime le nombre de messages voulus.
- crp = Active ou désactive le rich presence dynamique.
- rainbow = Ton pseudo change de toute les couleurs.
- rire = Ahahaha.
- memes", value=f"Envois un meme de reddit.
- nickrandom = Change le surnom d'un utilisateur du salon courant.
- screenshare [id du channel] = Renvois le lien pour faire un partage d'écran.
- baccalaureat = Affiche la probabilité que t'es ton bac.
- invitation = Renvois un lien d'invitation vers le serveur.
- note <note> = T'envois un message avec ta note.
- troll = Affiche une image troll.
- how_many = Affiche le nombre d'utilisateurs sur le serveur.
- syntax = Informations pour bien éditer son texte.
- sexe [butts/boobs] = Envois une image coquine. **(NSFW)**
- love <user1> [user2] = Découvre la probabilité que ces deux personnes se mettent en couple.
- delete", value='Envois une vidéo "Repost", alternative : `.repost`.
- nulle = Informe que le contenu précédent est nul (sous forme de vidéo).
- tagueule = Vidéo 'TG'.
- filsdepute = Vidéo 'FDP'.
- binary <texte> = Convertir le texte en binaire.
- citation <msgID/msgLink> [réponse] = Permet de citer un message et d'y répondre directement ou non.
- runtime = Affiche le temps depuis que le bot est en ligne.
- xd = Renvois un XD.
