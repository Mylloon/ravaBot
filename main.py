print("Chargement des fichiers requis...\n")

import discord
from discord.ext import tasks, commands
from random import randint, choice
import time
from time import sleep
import asyncio
import random
import datetime
import json
import os
import psycopg2
import re
import pickle

def set_variables(bot_=False, insulte_=False, mrs_=False, minigame_=False, starttime_=False):
	global client, token, CTX_RELOAD, cycle_RICHPRESENCE, have_rainbow, conn_DB
	global insulte_random
	global message_recently_deleted_msg, message_recently_deleted_aut
	global plusoumoins_enjeu
	global starttime
	if bot_==True:
		client = commands.Bot(command_prefix=".")
		token = "RENTRE TON TOKEN ICI"

		CTX_RELOAD=0
		cycle_RICHPRESENCE=False
		have_rainbow=False
		print("Connexion à la base de donnée...")
		try:
			conn_DB=psycopg2.connect("dbname='NOM DE TA BASE DE DONNEE' user='PSEUDO DE TA BASE DE DONNEE' host='IP DE TA BASE DE DONNEE' password='MOT DE PASSE DE TA BASE DE DONNEE'")
			print("Connexion a la base de donnée effectué.\n")
		except Exception as e:
			print("Impossible de se connecter a la base de donnée. Erreur:", e)

	if insulte_==True:
		insulte_random=False

	if mrs_==True:
		message_recently_deleted_msg=[]
		message_recently_deleted_aut=[]

	if minigame_==True:
		plusoumoins_enjeu=False

	if starttime_==True:
		starttime=datetime.datetime.now()

set_variables(True, True, True, True, True)

def JSONEncoder(o):
	if isinstance(o, datetime.datetime):
		return o.isoformat()

# Base de donnée ----- pour voir le tableau sql : SELECT * FROM users;

def update_db(arg=None):
	cur=conn_DB.cursor()
	if arg==None: #au lancement du bot, soit actualise la base de donnée au premier lancement, soit actualise le fichier users.json
		try:
			conn_DB.set_isolation_level(0)
			cur.execute("""CREATE TABLE users (
			id_user TEXT NOT NULL,
			dernier_message_XP_pics TEXT,
			experience INTEGER NOT NULL
			)""")
			print("Aucune table dans la base de donnée, création...")
			print("Table dans la base de donnée créée.")
			try:
				update_db("update")
				print("Actualisation de la base de donnée par rapport au fichier users.json effectué.\n")
			except:
				print("Echec lors de l'actualisation de la base de donnée par rapport au fichier users.json.\n")
		except Exception as e:
			if 'relation "users" already exists' in str(e):
				print("La table dans la base de donnée est déjà créée.\n")
				try:
					update_db("actualisation_usersJSON")
					print("Actualisation du fichiers users.json par rapport à la base de donnée effectué.\n")
					print("Connexion aux serveurs de Discord...")
				except:
					print("Echec lors de l'actualisation du fichiers users.json par rapport à la base de donnée.\n")
			else:
				print("Je ne peux pas préparer la base de données ! Erreur :", e, "\n")
	elif arg=="update": # actualise la base de donnée
		users=json.load(open('data/users.json', 'r'))
		cur.execute("""SELECT * FROM users""")
		rows = cur.fetchall()
		utlisateurs_in_db=[]
		for row in rows:
			utlisateurs_in_db.append(row[0])
		try:
			for key, value in users.items(): #value obligatoire
				if key in utlisateurs_in_db:
					cur.execute(f"""
					UPDATE users
					SET dernier_message_XP_pics = '{users[key]['dernier_message_XP_pics']}'
					, experience = {users[key]['experience']}
					WHERE id_user = '{key}'
					;
					""")
				else:
					cur.execute(f"""
					INSERT INTO users (
						id_user
						, dernier_message_XP_pics
						, experience
						)
					VALUES (
						'{key}'
						, '{users[key]['dernier_message_XP_pics']}'
						, {users[key]['experience']}
						);
					""")
		except Exception as e:
			print("Update de la base de donnée impossible. Erreur :", e, "\n")
	elif arg=="actualisation_usersJSON": # actualise le fichiers users.json en fonction de la base de donnée
		users=open("data/users.json","w")
		users.write("{\n")
		users.write("   \n")
		users.write("}")
		users.close()
		cur.execute("""SELECT * FROM users;""")
		rows = cur.fetchall()
		users=json.load(open('data/users.json', 'r'))
		for row in rows:
			users[str(row[0])]={}
			if row[1]!=None:
				users[str(row[0])]['dernier_message_XP_pics']=str(row[1])
			if row[2]!=None:
				users[str(row[0])]['experience']=row[2]
			json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)

update_db() #création de la base de donnée ou update du fichiers users.json

# Tasks

@tasks.loop(seconds=60.0)
async def updater():
	update_db("update")

@updater.before_loop
async def before_updater():
	await client.wait_until_ready()

updater.start()

@client.event
async def on_connect():
	temps_latence_lancement=int(time.strftime("%S"))-temps_lantence_avant
	print(f"Client connecté à Discord (en {temps_latence_lancement} seconde{'s' if temps_latence_lancement>=2 else ''}).\n")

@client.event
async def on_resume():
	print("Le client est de nouveau connecté.")

@client.event
async def on_ready():
	global CTX_RELOAD
	await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="le bon rhum de Binks", type=discord.ActivityType.listening))
	H=int(time.strftime("%H"))+1
	print("Bot prêt. Le",time.strftime(f"%d/%m/%Y à {H}:%M:%S"),"!")
	if CTX_RELOAD!=0:
		await CTX_RELOAD.send("** **\nJe suis de retour !")
		CTX_RELOAD=0

@client.event
async def on_member_join(member):
	if member.bot==True:
		role=discord.utils.get(member.guild.roles, name="🤖 Bot")
	else:
		role=discord.utils.get(member.guild.roles, name="👤 Invité")
	await member.add_roles(role)
	try:
		await member.send(f"Bienvenue à toi **{member.name}** sur le serveur {member.guild.name} !\n\nTu as obtenu le rôle **{role}** !")
	except:
		pass
	if member.guild.id==634051485218373636: #ravag
		channel=client.get_channel(634052995771924480) #Salon #général
		await channel.send(f"Another **fag** joined the chat ({member.mention})", file=discord.File("files/welcome.mp4"))

@client.event
async def on_member_remove(member):
	channel=client.get_channel(634087376687333377) #Salon #notif-arrivé-départ
	await channel.send(f"➡️ **{member.mention}** a quitté le serveur.")

@client.event
async def on_message(message):
	await client.process_commands(message)
	messchan=str(message.channel)
	if messchan.startswith("Direct Message with"): # envoi du message en dm
		messcont=str(message.content)
		if "désolé mais je ne communique pas en message privé. N'hésites pas a me rejoindre sur le serveur des ravaG !" not in messcont:
			if "-- SUGGESTION DE" not in messcont:
				if "Bienvenue à toi" not in messcont:
					if "-- NOTE --" not in messcont:
						if message.author.bot==False:
							await message.channel.send(f"Bonjour {message.author.name}, désolé mais je ne communique pas en message privé. N'hésites pas a me rejoindre sur le serveur des ravaG !\nVoici le lien d'invitation : https://discord.gg/ZZC557c")
	if messchan.startswith("Direct Message with"):
		return
	if message.author==client.user:
		return
	if randint(1,10)<=3 and message.content.startswith(".")!=True and insulte_random==True and message.content.startswith("!")!=True:
		
		auteur=(message.author.name).replace("[ravaG] ", "")
		INSULTES=[f"Ta gueule {auteur}", "Ca t'arrives de te taire ?", "Cause toujours tu m'intéresses...", "Mais t'es con ?", "Bah nique ta mère alors", "Mange tes morts", "Deterre tes morts",
		"Au pire mange moi le poirot ?", "Nan sérieux tu fais pitié là stp j'vais t'mute x)))", "k", "Enfant de gang bang, va.", f'"*{message.content}*" Tu fais pitié sérieux...', "J'vais te bukkake tes morts",
		"Sustente toi de tes défunts", "DEMARRE_TA_MERE", "Je t'ai jamais aimé t'façon"]
		insult=random.choice(INSULTES)
		if insult=="DEMARRE_TA_MERE":
			await message.channel.send("Tiens c'est pour démarrer ta mère", file=discord.File("files/car_key.png"))
		else:
			await message.channel.send(f"{insult}")
	if message.author.bot!=True:
		if message.content.startswith(".")!=True and message.content.startswith("!")!=True:
			users=json.load(open('data/users.json', 'r'))
			try:
				XP_User=users[str(message.author.id)]['experience']
				dernier_message_temps=users[str(message.author.id)]['dernier_message_XP_pics']
				dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
				ecart=message.created_at-dernier_message_temps #caclul l'écart
			except:
				users[str(message.author.id)]={}
				XP_User=0
				ecart=datetime.timedelta(seconds=16) #au premier message, lecart est suffisant pour que l'user gagne de l'xp
			if ecart.seconds>=15:
				XP_User+=randint(3,13)
				users[str(message.author.id)]['experience']=XP_User
				users[str(message.author.id)]['dernier_message_XP_pics']=message.created_at
				json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)

@client.event
async def on_message_delete(message):
	if not message.author==client.user:
		if not message.content.startswith(".suggestion"):
			listechannel(message)
			if message.channel.id in LchannelID:
				if len(message.content)<1 or len(message.author.name)<1:
					return
				if len(message_recently_deleted_msg)>=3:
					del message_recently_deleted_msg[0]
				if len(message_recently_deleted_aut)>=3:
					del message_recently_deleted_aut[0]
				message_recently_deleted_msg.append(message.content)
				message_recently_deleted_aut.append(message.author)

@client.event
async def on_command_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"La commande nécessite un ou plusieurs argument, `.help` pour plus d'informations.")
	if isinstance(error, commands.CommandNotFound):
		commande=str(error).replace('Command "',"").replace('" is not found','')
		if commande=="stop":
			suggestion=f"Tu peux essayé la commande `.eteindre`."
		elif commande=="suggestions":
			suggestion=f"Tu peux essayé la commande `.suggestion`."
		elif commande=="aide":
			suggestion=f"Tu peux essayé la commande `.help`."
		elif commande=="calculer" or commande=="calcul" or commande=="calcule":
			suggestion=f"Tu peux essayé la commande `.calc`."
		elif commande=="jvousnike" or commande=="jvounike"  or commande=="jvounik" :
			suggestion=f"Tu peux essayé la commande `.jvousnik`."
		else:
			suggestion=""
		if commande.startswith(".")!=True:
			await ctx.send(f"La commande *.{commande}* n'existe pas ! {suggestion}", delete_after=3)
	if len(str(error))>2000:
		await ctx.send(f"**Conflit avec Discord, veuillez réessayer plus tard.**")

@client.command()
async def ping(ctx):
	await ctx.send(f"Pong! ({round(client.latency * 1000)}ms)")

@client.command(aliases=['8ball','8b'])
async def _8ball(ctx, *, question):
	reponses=["C'est sûr.","Il en est décidément ainsi.","Incontestablement.","Oui, sans aucun doute.","Vous pouvez vous y fier.","Tel que je le vois, oui.","C'est le plus probable.",
	"Cela montre de bonnes perspectives","Certes.","Les signes indiquent que oui.","Ma réponse est oui.","Ta question est trop floue, réessaie.","Redemandes plus tard.",
	"Je ferais mieux de pas te le dire maintenant.","Je ne peux pas le prédire actuellement.","Concentrez-vous et redemandez.","N'y comptes pas trop.","Ma réponse est non.","Mes sources disent non.",
	"Les perspectives ne sont pas si bonnes.","C'est très douteux.","hmm..","Menteur."]
	await ctx.send(f"`{random.choice(reponses)}`")

@client.command()
async def eteindre(ctx):
	global cycle_RICHPRESENCE
	listeadminBot(ctx)
	if ctx.author in LadminBot:
		await ctx.send("C'est donc ainsi... bye-bye ! :sleeping:")
		cycle_RICHPRESENCE=False
		await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name="s'éteindre...", type=discord.ActivityType.playing))
		print("Déconnexion dans 5 secondes...")
		await asyncio.sleep(5)
		print("Déconnexion effectué le",time.strftime("%d/%m/%Y à %H:%M:%S"),f"par @{ctx.author} !")
		await client.close()
	else:
		await ctx.send("Tu ne peux pas m'éteindre aussi facilement :stuck_out_tongue_closed_eyes: !!")

@client.command()
async def ir(ctx):
	global insulte_random
	listeadminBot(ctx)
	if ctx.author in LadminBot:
		if insulte_random==False:
			insulte_random=True
		else:
			insulte_random=False
		await ctx.send(f"La réponse random est maintenant {str(insulte_random).replace('True', 'activé').replace('False', 'désactivé')}.")
	else:
		await ctx.send("Tu ne peux pas faire ça.")

@client.command()
async def ppc(ctx, *, choix):
	ordi=randint(1,3) #1: pierre, 2: papier, 3: ciseaux
	if ordi==1:
		ordi="pierre"
	elif ordi==2:
		ordi="papier"
	elif ordi==3:
		ordi="ciseaux"
	if choix=="pierre" or choix=="Pierre":
		if ordi=="pierre":
			await ctx.send(f"J'ai fait {ordi}, égalité !")
		elif ordi=="papier":
			await ctx.send(f"J'ai fait {ordi}, tu as perdu !")
		elif ordi=="ciseaux":
			await ctx.send(f"J'ai fait {ordi}, tu as gagné !")
	elif choix=="papier" or choix=="Papier":
		if ordi=="pierre":
			await ctx.send(f"J'ai fait {ordi}, tu as gagné !")
		elif ordi=="papier":
			await ctx.send(f"J'ai fait {ordi}, égalité !")
		elif ordi=="ciseaux":
			await ctx.send(f"J'ai fait {ordi}, tu as perdu !")
	elif choix=="ciseaux" or choix=="Ciseaux":
		if ordi=="pierre":
			await ctx.send(f"J'ai fait {ordi}, tu as perdu !")
		elif ordi=="papier":
			await ctx.send(f"J'ai fait {ordi}, tu as gagné !")
		elif ordi=="ciseaux":
			await ctx.send(f"J'ai fait {ordi}, égalité !")
	else:
		await ctx.send("Respecte les choix : Pierre, papier, ou ciseaux ?")

@client.command(aliases=['suggest'])
async def suggestion(ctx, *, suggest):
	if len(suggest)<=10:
		await ctx.send("Ta suggestion doit au moins faire 10 caractères.")
	else:
		await ctx.channel.purge(limit=1)
		await ctx.send(f"Merci pour ta suggestion {ctx.author.name} !", delete_after=2)
		listeadminBot(ctx)
		n=len(LadminBot)
		while n!=0:
			adminUser=client.get_user(LadminBot[n-1].id)
			await adminUser.send(f"** -- SUGGESTION DE {ctx.author.mention} ({ctx.author.name}) --**\n\n `{suggest}`")
			n-=1

client.remove_command("help")
@client.command(aliases=['aide'])
async def help(ctx, *, page="1"):
	ravaBot=client.get_user(571348123855880192)
	if page=="music" or page=="xp":
		embed=discord.Embed(title=f"Commandes de {ravaBot.name} - page {page} (certaines commandes peuvent être réservés au staff)", colour=discord.Colour.green())
		embed.set_footer(text=f"Développé par des ravaG. - .help [page/music/xp] ({page})")
		if page=="music": #10
			embed.add_field(name=".connect [id du channel]", value="Se connecte au salon vocal.", inline=False)
			embed.add_field(name=".play <musique>", value="Recherche une chanson sur Youtube et l'ajoute à la file d'attente.", inline=False)
			embed.add_field(name=".pause", value="Mets en pause de la chanson en cours de lecture.", inline=False)
			embed.add_field(name=".resume", value="Reprends la chanson en pause.", inline=False)
			embed.add_field(name=".skip", value="Passe la chanson.", inline=False)
			embed.add_field(name=".queue", value="Affiche la file d'attente des chansons à venir.", inline=False)
			embed.add_field(name=".now_playing", value="Affiche des informations sur la chanson en cours de lecture.", inline=False)
			embed.add_field(name=".volume <valeur>", value=f"Modifiez le volume de <@{ravaBot.id}> (entre 1 et 100).", inline=False)
			embed.add_field(name=".disconnect", value="Arrête la chanson en cours de lecture et quitte le salon vocal.", inline=False)
			embed.add_field(name=".lyrics [song]", value="Affiche les paroles d'une chanson.", inline=False)
		if page=="xp": #5
			embed.add_field(name=".xp leaderboard", value="Affiche le top 5 du serveur.", inline=False)
			embed.add_field(name=".xp info", value="Affiche les infos relatives à l'xp.", inline=False)
			embed.add_field(name=".xp clear", value="Supprime l'XP d'un utilisateur.", inline=False)
			embed.add_field(name=".xp backup", value="Envoie une backup en .json des levels des utilisateurs.", inline=False)
			embed.add_field(name=".xp give", value="Permet d'ajouter (ou de retirer si valeur négative) de l'xp à un utilisateur.", inline=False)
		await ctx.send(embed=embed)
	else:
		try:
			page=int(page)
		except:
			page=1
		pagetot=5
		embed=discord.Embed(title=f"Commandes de {ravaBot.name} - page {page}/{pagetot}", colour=discord.Colour.green())
		embed.set_footer(text=f"Développé par des ravaG. - .help [page/music/xp] ({page}/{pagetot})")
		if page==1: #10/10
			embed.add_field(name=".help [page=1/music/xp]", value="Affiche le menu d'aide des commandes.", inline=False)
			embed.add_field(name=".avatar [user]", value="Affiche ton avatar ou celui que tu mentionnes.", inline=False)
			embed.add_field(name=".kiss", value="Fait un bisou à un inconnu.", inline=False)
			embed.add_field(name=".deglingue", value="Tu déglingues un inconnu (ou pas).", inline=False)
			embed.add_field(name=".suggestion <message de suggestion>", value="Pour proposé une fonctionnalité.", inline=False)
			embed.add_field(name=".ppc <pierre/papier/ciseaux>", value=f"Un simple Chifumi contre <@{ravaBot.id}>.", inline=False)
			embed.add_field(name=".ping", value="Pong!", inline=False)
			embed.add_field(name=".iq", value="Calcule ton IQ.", inline=False)
			embed.add_field(name=".chatclear", value="Clear le canal de discussion.", inline=False)
			embed.add_field(name=".eteindre", value=f"Éteint <@{ravaBot.id}>.", inline=False)
		elif page==2: #10/10
			embed.add_field(name=".8ball <question>", value="Répond a ta question.", inline=False)
			embed.add_field(name=".trueid <id>", value="Renvois à l'utilisateur correspondant.", inline=False)
			embed.add_field(name=".calc <calcul>", value="Calcule une expression.", inline=False)
			embed.add_field(name=".mrs", value="Affiche les messages récemment supprimés.", inline=False)
			embed.add_field(name=".reload", value=f"Redémarre <@{ravaBot.id}>.", inline=False)
			embed.add_field(name=".ir", value="Active ou désactive la réponse automatique.", inline=False)
			embed.add_field(name=".jvousnik", value="J'VOUS NIQUE !", inline=False)
			embed.add_field(name=".plusoumoins", value="Un plus ou moins entre 1 et 100.", inline=False)
			embed.add_field(name=".vidage", value="Supprime touts tes messages (uniquement dans le salon <#634059175004995587>).", inline=False)
			embed.add_field(name=".delchat <nombre>", value="Supprime le nombre de messages voulus.", inline=False)
		elif page==3: #10/10
			embed.add_field(name=".crp", value="Active ou désactive le rich presence dynamique.", inline=False)
			embed.add_field(name=".rainbow", value="Ton pseudo change de toute les couleurs.", inline=False)
			embed.add_field(name=".rire", value="Ahahaha.", inline=False)
			embed.add_field(name=".memes", value=f"Envois un meme de reddit.", inline=False)
			embed.add_field(name=".nickrandom", value="Change le surnom d'un utilisateur du salon courant.", inline=False)
			embed.add_field(name=".screenshare [id du channel]", value="Renvois le lien pour faire un partage d'écran.", inline=False)
			embed.add_field(name=".baccalaureat", value="Affiche la probabilité que t'es ton bac.", inline=False)
			embed.add_field(name=".invitation", value="Renvois un lien d'invitation vers le serveur.", inline=False)
			embed.add_field(name=".note <note>", value="T'envois un message avec ta note.", inline=False)
			embed.add_field(name=".troll", value="Affiche une image troll.", inline=False)
		elif page==4: #10/10
			embed.add_field(name=".how_many", value="Affiche le nombre d'utilisateurs sur le serveur.", inline=False)
			embed.add_field(name=".syntax", value="Informations pour bien éditer son texte.", inline=False)
			embed.add_field(name=".sexe [butts/boobs]", value="Envois une image coquine. **(NSFW)**", inline=False)
			embed.add_field(name=".love <user1> [user2]", value="Découvre la probabilité que ces deux personnes se mettent en couple.", inline=False)
			embed.add_field(name=".delete", value='Envois une vidéo "Repost", alternative : `.repost`.', inline=False)
			embed.add_field(name=".nulle", value="Informe que le contenu précédent est nul (sous forme de vidéo).", inline=False)
			embed.add_field(name=".tagueule", value="Vidéo 'TG'.", inline=False)
			embed.add_field(name=".filsdepute", value="Vidéo 'FDP'.", inline=False)
			embed.add_field(name=".binary <texte>", value="Convertir le texte en binaire.", inline=False)
			embed.add_field(name=".citation <msgID/msgLink> [réponse]", value="Permet de citer un message et d'y répondre directement ou non.", inline=False)
		elif page==5: #2/10
			embed.add_field(name=".runtime", value="Affiche le temps depuis que le bot est en ligne.", inline=False)
			embed.add_field(name=".xd", value="Renvois un XD.", inline=False)
		else:
			embed.add_field(name="Rien a affiché.", value="Essai une page différente, ou alors `.help music/xp`.", inline=False)
		await ctx.send(embed=embed)

@client.command()
async def deglingue(ctx):
	delingue_name=["Clément","Mathéo","Anri","Arthur","toutes les meufs de paname","personne (pucot4life)","Mathieu","MLP","Lucie","Campestrimoche","la daronne à turure", "la daronne à mymy"]
	n=randint(0,len(delingue_name)-1)
	i=randint(0,9)
	if i==0:
		await ctx.send("Crocodile la pute de Luffy")
	else:
		await ctx.send(f"{ctx.author.mention} déglingue {delingue_name[n]} !!")

@client.command()
async def kiss(ctx):
	Liste=ctx.channel.members #liste de tous les membres du channel
	Liste.remove(ctx.author) #on retire l'auteur du message de la liste
	user_kissed=choice(Liste) #on prend un membre au hasard
	while user_kissed.bot==True: #on check que c'est pas un bot
		user_kissed=choice(Liste)
	await ctx.send(f"{ctx.author.mention} fait un bisous baveux à {user_kissed.mention}")

@client.command(aliases=['clearchat','cc'])
async def chatclear(ctx):
	listeravaG(ctx)
	if ctx.author in LravaG:
		await ctx.send(f"**\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n**\n*Chat clear par {ctx.author.name} avec succès !*")
	else:
		await ctx.send("Tu ne peux pas faire ça.")

@client.command()
async def iq(ctx, *, user='0'):
	if user=='0':
		user=ctx.author
		return await ctx.send(f"T'as {randint(randint(-100,0),220)} IQ {user.mention} !")
	else:
		try:
			user2=user
			user2=user2[2:-1]
			user2=user2.replace("!","")
			user2=int(user2)
			user2=client.get_user(user2)
			ravaBot=client.get_user(571348123855880192)
			if user2.id == ravaBot.id:
				return await ctx.send(f"Bah... pas ouf... j'ai juste 100000 IQ !")
			else:
				return await ctx.send(f"{user2.mention} as {randint(randint(-100,0),220)} IQ  !")
		except:
			return await ctx.send(f"{user} as {randint(randint(-100,0),220)} IQ  !")

@client.command()
async def avatar(ctx, *, user='0'):
	if user=='0':
		user=ctx.author
	else:
		user=user[2:-1]
		user=user.replace("!","")
		user=int(user)
		user=client.get_user(user)
	await ctx.send(f"Photo de profil de {user.mention} : {user.avatar_url}")

@client.command()
async def trueid(ctx, *, id='0'):
	if id=='0':
		await ctx.send("ID manquante.")
	else:
		id=int(id)
		id=client.get_user(id)
		await ctx.send(f"Voici l'utilisateur en question : {id}")

@client.command()
async def calc(ctx, *, msg):
	equation = msg.replace('^', '**').replace('x', '*').replace('×', '*').replace('÷', '/').replace('≥', '>=').replace('≤', '<=')
	try:
		try:
			if '=' in equation:
				if '<' in equation:
					left = eval(equation.split("<=")[0])
					right = eval(equation.split("<=")[1])
					answer = str(left <= right)
				elif '>' in equation:
					left = eval(equation.split(">=")[0])
					right = eval(equation.split(">=")[1])
					answer = str(left >= right)
				else:
					left = eval(equation.split("=")[0])
					right = eval(equation.split("=")[1])
					answer = str(left == right)
			else:
				answer = str(eval(equation))
		except ZeroDivisionError:
			return await ctx.send("Tu ne peux pas divisé par 0.")
	except TypeError:
		return await ctx.send("Requête de calcul invalide.")
	if '.' in answer:
		aftercomma = answer.split(".")[1]
		if len(aftercomma)>2:
			answer = str(round(float(answer),2))
			equation=f"'{equation}' arrondi à 2"
	equation=equation.replace('*', '×').replace('/', '÷').replace('>=', '≥').replace('<=', '≤')
	embed=discord.Embed(color=0xD3D3D3, title='Calculatrice')
	embed.set_footer(text=ctx.author)

	embed.add_field(name='Calcul :', value=equation, inline=False)
	embed.add_field(name='Réponse :', value=answer.replace('False', 'Faux').replace('True', 'Vrai'), inline=False)
	await ctx.send(content=None, embed=embed)
	await ctx.message.delete()

@client.command()
async def mrs(ctx):
	listeravaG(ctx)
	listeadminBot(ctx)
	if ctx.author in LravaG or ctx.author in LadminBot:
		if len(message_recently_deleted_msg)==0:
			couleur=discord.Colour.red()
		else:
			couleur=discord.Colour.blue()
		embed=discord.Embed(title="Messages récemment supprimés", colour=couleur)
		embed.set_footer(text="Développé par des ravaG.")

		if len(message_recently_deleted_msg)==0:
			embed.add_field(name="Aucun message récemment supprimé", value="Réessaie plus tard.", inline=False)
		else:
			for i in range (len(message_recently_deleted_msg)):
				embed.add_field(name=message_recently_deleted_msg[i], value=message_recently_deleted_aut[i], inline=False)
		await ctx.send(embed=embed)
	else:
		await ctx.send("Tu ne peux pas faire ça.")

@client.command()
async def reload(ctx):
	global CTX_RELOAD, cycle_RICHPRESENCE
	listeadminBot(ctx)
	if ctx.author in LadminBot:
		await ctx.send("Je reviens tout de suite ! :smile:")
		cycle_RICHPRESENCE=False
		await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name="redémarrer...", type=discord.ActivityType.playing))
		print("Déconnexion dans 5 secondes...")
		await asyncio.sleep(5)
		print("Déconnexion effectué le",time.strftime("%d/%m/%Y à %H:%M:%S"),"!")
		print("Rédemarrage dans 3 secondes...")
		sleep(3)
		client.clear()
		set_variables(False, True, True, False, True)
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		print("Rédemarré le",time.strftime("%d/%m/%Y à %H:%M:%S"),f"par @{ctx.author}.")
		CTX_RELOAD=ctx.channel
		await client.connect()
	else:
		await ctx.send("Tu ne peux pas me redémarrer.")

@client.command()
async def jvousnik(ctx):
	await ctx.send("J'vous nique !", tts=True)

@client.command()
async def xp(ctx, *, user='0'):
	if user=="leaderboard" or user=="leader" or user=="top" or user=="toplevel" or user=="leveltop" or user=="lead":
		leaderboardXP()

		embed=discord.Embed(title=f"**Leaderboard de {ctx.guild.name}**", colour=discord.Colour.gold())
		embed.set_footer(text="Développé par des ravaG.")

		n=len(XP_USER_LEADERBOARD)
		if n!=0:
			for i in range(0,len(XP_USER_LEADERBOARD)):
				levelUser=rankXP(int(XP_USER_LEADERBOARD[n-1]))
				embed.add_field(name=f"{i+1}. Niveau {levelUser} avec {XP_retour_user(XP_USER_LEADERBOARD[n-1])} XP ↴", value=f"<@{NAMES_USER_LEADERBOARD[n-1]}>", inline=False)
				i+=1
				n-=1
		else:
			embed.add_field(name="Aucune personne dans la leaderboard", value="** **", inline=False)
		await ctx.send(embed=embed)
	elif user=="info" or user=="aide" or user=="help":
		embed=discord.Embed(title="**Infos sur l'XP**", colour=discord.Colour.greyple())
		embed.set_footer(text="Développé par des ravaG.")

		embed.add_field(name="Gagné de l'XP ?", value="Gagnable toutes les 15 secondes.\nPossibilité d'en gagné entre 3 et 13 par messages.", inline=False)
		embed.add_field(name=".xp [user]", value="Pour connaître l'XP d'un utilisateur et son niveau.", inline=False)
		embed.add_field(name=".xp", value="Pour connaître sa quantité d'XP et son niveau.", inline=False)
		embed.add_field(name=".xp leaderboard", value="Affiche la leaderboard du serveur.", inline=False)
		embed.add_field(name=".xp info", value="Affiche ceci.", inline=False)

		await ctx.send(embed=embed)
	elif user.startswith("clear"):
		listeadminBot(ctx)
		if ctx.author in LadminBot:
			try:
				user=user[6:]
				user=user[2:-1]
				user=user.replace("!","")
				user=client.get_user(int(user))
			except:
				return await ctx.send("Merci de renseigné un utilisateur valide.")
			users=json.load(open('data/users.json', 'r'))
			try:
				try:
					OLD_XP_USER=users[str(ctx.author.id)]['experience']
				except:
					OLD_XP_USER=0
				users[str(ctx.author.id)]['experience']=0
				json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
				return await ctx.send(f"Expérience de {user.mention} supprimée. ({XP_retour_user(OLD_XP_USER)} XP supprimé.)")
			except:
				return await ctx.send(f"{user.mention} n'as pas d'XP.")
		else:
			return await ctx.send("Tu ne peux pas faire ceci.")
	elif user.startswith("backup"):
		listeadminBot(ctx)
		if ctx.author in LadminBot:
			return await ctx.send(file=discord.File(f"data/users.json"))
		else:
			return await ctx.send("Tu ne peux pas faire ceci.")
	elif user.startswith("give"):
		listeadminBot(ctx)
		if ctx.author in LadminBot:
			try:
				user=user[6:]
				user=user.split(" ")
				userNAME=user[0]
				userNAME=userNAME[2:-1]
				userNAME=userNAME.replace("!","")
				userNAME=client.get_user(int(userNAME))
				userXPtoGIVE=user[-1]
				userXPtoGIVE=userXPtoGIVE.replace("xp","")
			except:
				return await ctx.send("Merci de renseigné un utilisateur ou une xp valide. Rappel : `.xp give <user> <xp>`")
			try:
				users=json.load(open('data/users.json', 'r'))
				try:
					XP_User=users[str(userNAME.id)]['experience']
				except:
					XP_User=0
				XP_User+=int(userXPtoGIVE)
				users[str(userNAME.id)]['experience']=XP_User
				json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
				if int(userXPtoGIVE)<0:
					userXPtoGIVE=int(userXPtoGIVE)*-1
					return await ctx.send(f"Expérience de {userNAME.mention} mis à jour, retrait de {XP_retour_user(userXPtoGIVE)} xp. {userNAME.mention} a désormais {XP_retour_user(XP_User)} xp.")
				else:
					return await ctx.send(f"Expérience de {userNAME.mention} mis à jour, ajout de {XP_retour_user(userXPtoGIVE)} xp. {userNAME.mention} a désormais {XP_retour_user(XP_User)} xp.")
			except:
				return await ctx.send(f"{userNAME.mention} n'as pas encore d'XP.")
		else:
			return await ctx.send("Tu ne peux pas faire ceci.")
	else:
		if user=='0':
			user=ctx.author
		else:
			user=user[2:-1]
			user=user.replace("!","")
			try:
				user=int(user)
			except:
				return await ctx.send("Erreur d'arguments.")
			user=client.get_user(user)
			if user.bot==True:
				return await ctx.send("Un bot ne peux pas obtenir d'XP.")
		try:
			users=json.load(open('data/users.json', 'r'))
			XP_User=users[str(user.id)]['experience']
		except:
			XP_User=0

		await ctx.send(f"{user.mention} a {XP_User} XP (niveau {rankXP(XP_User)}) !")

def rankXP(xp):
	n=1
	while xp>=5*(n-1)**2+100+50*(n-1):
		n+=1
	return n

def XP_retour_user(xp):
	try:
		if xp>=1000000000:
			xp=(f"{round(xp/1000000000, 1)}Ma")
	except:
		pass
	try:
		if xp>=1000000:
			xp=(f"{round(xp/1000000, 1)}Mi")
	except:
		pass
	try:
		if xp>=1000:
			xp=(f"{round(xp/1000, 1)}k")
	except:
		pass
	return xp

def leaderboardXP():
	global XP_USER_LEADERBOARD, NAMES_USER_LEADERBOARD
	users=json.load(open('data/users.json', 'r'))
	NAMES=[]
	XP=[]
	for key, value in users.items(): #value obligatoire
		if key!="571348123855880192":
			NAMES.append(key)
			XP.append(users[key]['experience'])
	data=[]

	for i in range (0,len(XP)):
		data.append((XP[i], NAMES[i]))

	data.sort(reverse=False) #trier a l'envers (du + nul au meilleur)

	XP_USER_LEADERBOARD=[]
	NAMES_USER_LEADERBOARD=[]

	for xpU, nom in data:
		XP_USER_LEADERBOARD.append(xpU)
		NAMES_USER_LEADERBOARD.append(nom)

	while len(XP_USER_LEADERBOARD)>=6: #n'affiche que les 5 premiers
		del XP_USER_LEADERBOARD[0]
		del NAMES_USER_LEADERBOARD[0]

@client.command()
async def crp(ctx):
	global cycle_RICHPRESENCE
	listeadminBot(ctx)
	if ctx.author in LadminBot:
		if cycle_RICHPRESENCE==True:
			cycle_RICHPRESENCE=False
			await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="le bon rhum de Binks", type=discord.ActivityType.listening))
			await ctx.send("Le changement de rich presence est désormais désactivé.")
		else:
			cycle_RICHPRESENCE=True
			await ctx.send("Le changement de rich presence est désormais activé.")
			while cycle_RICHPRESENCE==True:
				t=30 #délai entre chaque changement
				await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="pikachu qui dance", type=discord.ActivityType.watching))
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="Diablo IV", type=discord.ActivityType.playing))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="Flex Air", type=discord.ActivityType.listening))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="GTA VI", type=discord.ActivityType.playing))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="r/dankmemes ¯\\_(ツ)_/¯", type=discord.ActivityType.watching))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="les cris de Sardoche", type=discord.ActivityType.listening))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="les nudes de turure", type=discord.ActivityType.watching))
				else:
					return
				await asyncio.sleep(t)
				if cycle_RICHPRESENCE==True:
					await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="le bon rhum de Binks", type=discord.ActivityType.listening))
				else:
					return
				await asyncio.sleep(t)
	else:
		return await ctx.send("Tu ne peux pas faire ceci.")

@client.command(aliases=['+ou-', '+-'])
async def plusoumoins(ctx):
	global plusoumoins_enjeu
	if plusoumoins_enjeu==False:
		plusoumoins_enjeu=True
		number = randint(1,100)
		guess = 5
		while guess!=0:
			try:
				if ctx.content==ctx.author:
					await ctx.send("Choisis un nombre entre 1 et 100.")
			except:
				await ctx.send("Choisis un nombre entre 1 et 100.")
			try:
				msg = await client.wait_for('message', timeout=30)
			except asyncio.TimeoutError:
				return await ctx.send(f"Tu as mis trop de temps a répondre. La réponse était {number}.")
			if msg.author==ctx.author:
				if msg.content=="stop":
					plusoumoins_enjeu=False
					return await ctx.send(f"Fin du plus ou moins. La réponse était {number}.")
				try:
					attempt = int(msg.content)
					if attempt > number:
						if guess-1!=0:
							await ctx.send(f"J'pense que c'est moins... Il te reste {guess-1} essai{'s' if guess-1>1 else ''}.")
						guess -= 1
					elif attempt < number:
						if guess-1!=0:
							await ctx.send(f"J'pense que c'est plus... Il te reste {guess-1} essai{'s' if guess-1>1 else ''}.")
						guess -=1
					elif attempt == number:
						users=json.load(open('data/users.json', 'r'))
						try:
							XP_User=users[str(ctx.author.id)]['experience']
						except:
							users[str(ctx.author.id)]={}
							XP_User=0
						if guess==1:
							don_xp=50
						if guess==2:
							don_xp=60
						if guess==3:
							don_xp=80
						if guess==4:
							don_xp=100
						if guess==5:
							don_xp=150
						XP_User+=don_xp
						users[str(ctx.author.id)]['experience']=XP_User
						json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
						plusoumoins_enjeu=False
						return await ctx.send(f"Tu as trouvé, bien joué ! {don_xp} xp ont été ajouté a ton compte !")
				except:
					await ctx.send("Erreur dans la réponse, merci de n'écrire qu'un nombre. Tapez `stop` pour arrêter le jeu.")
		plusoumoins_enjeu=False
		await ctx.send(f"T'as pas trouvé... dommage, c'était {number}.")

@client.command()
async def rainbow(ctx, *, user="0"):
	global have_rainbow
	listeadminBot(ctx)
	if ctx.author in LadminBot:
		if user=="start":
			if have_rainbow==False:
				have_rainbow=True
				return await ctx.send("Le rainbow est lancé.")
			else:
				return await ctx.send("Le rainbow est déjà lancé.")
		if user=="stop":
			if have_rainbow==True:
				role=discord.utils.get(ctx.guild.roles, name="RAINBOW")
				for member in ctx.guild.members:
					if role in member.roles:
						await member.remove_roles(role)
				have_rainbow=False
				return await ctx.send("Le rainbow est arrêté.")
			else:
				return await ctx.send("Le rainbow n'est pas lancé.")
		if user=="0":
			if have_rainbow==False:
				return await ctx.send("Tu dois lancer le rainbow avant toute chose. `.rainbow start`")
		if user!="start" or user!="stop":
			if have_rainbow==True:
				if user=="0":
					user=ctx.author
				else:
					try:
						user=user.replace("<","")
						user=user.replace(">","")
						user=user.replace("@","")
						user=user.replace("!","")
						user=ctx.guild.get_member(int(user))
					except:
						return await ctx.send("Merci de renseigné un utilisateur valide.")
				role=discord.utils.get(ctx.guild.roles, name="RAINBOW")
				Lrainbow=[]
				for member in ctx.guild.members:
					if role in member.roles:
						Lrainbow.append(member)
				if user in Lrainbow:
					await user.remove_roles(role)
					await ctx.send(f"Le rainbow pour {user.mention} est désactivé.")
				else:
					await user.add_roles(role)
					await ctx.send(f"Le rainbow pour {user.mention} est activé.")
				colours=[0xE74C3C, 0x2ECC71, 0x3498DB, 0xE67E22, 0x1ABC9C]
				i=0
				while have_rainbow==True:
					i=(i+1)%len(colours)
					await role.edit(colour=discord.Colour(colours[i]))
					await asyncio.sleep(1)
			else:
				return await ctx.send("Tu dois lancer le rainbow avant toute chose. `.rainbow start`")
	else:
		return await ctx.send("Tu ne peux pas faire ceci.")

@client.command()
async def rire(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_rire']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		ecart=datetime.timedelta(seconds=6) #au premier message, lecart est suffisant pour que l'user gagne de l'xp
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_rire']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		rigolade=["AHAHAHAHAHAHAHAHAH", "JADORE_RIRE", "XPTDRRRRRRR MDRRRRR DES BARRES DE RIRE !!!", "ENORME_RIGOLADE"]
		rigolade=choice(rigolade)
		await ctx.message.delete()
		if rigolade=="JADORE_RIRE":
			return await ctx.send(file=discord.File("files/jadore_rire.webm"))
		if rigolade=="ENORME_RIGOLADE":
			return await ctx.send(file=discord.File("files/enorme_rigolade.mp4"))
		else:
			return await ctx.send(f"{rigolade}")
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command(aliases=['nr'])
async def nickrandom(ctx):
	listeravaG(ctx)
	if ctx.author in LravaG:
		Liste=ctx.channel.members
		Liste.remove(ctx.author)
		user_nicked=choice(Liste)
		while user_nicked.bot==True or ctx.author==user_nicked:
			user_nicked=choice(Liste)
		random_nick=["BlackBathevi0r", "Turure", "Mylloon", "DJ Tanoz", "Azazoul", "Monstre2Sexe", "xD4rkS4suk3x", "P'tite salope", "U'r mom is garbage"]
		random_nick=choice(random_nick)
		await ctx.send(f"{user_nicked.mention} s'appelle maintenant {random_nick}")
		await user_nicked.edit(nick=random_nick)
	else:
		return await ctx.send("Tu ne peux pas faire ceci.")

try:
	client.load_extension("cogs.meme")
except Exception as error:
	print(error)

try:
	client.load_extension("cogs.music")
except Exception as error:
	print(error)

try:
	client.load_extension("cogs.nsfw")
except Exception as error:
	print(error)

@client.command(aliases=['ss'])
async def screenshare(ctx, *, channel: discord.VoiceChannel=None):
	if not channel:
		try:
			channel = ctx.author.voice.channel
		except AttributeError:
			return await ctx.send("Aucun channel à rejoindre. Veuillez spécifier un channel valide ou rejoindre un channel.")
	return await ctx.send(f"**{channel}** : https://discordapp.com/channels/{ctx.guild.id}/{channel.id}")

@client.command(aliases=['baccalaureat']) # Tout les XXXXXXX étaient des id de compte Discord.
async def bac(ctx):
	avis_bac=1
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(0,20)
		return await ctx.send(f"T'as pas eu ton bac, c'est bien dommage.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(80,100)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(1,1) else ' pas'}. Bonne chance pour les rattrapages !")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(50,90)
		return await ctx.send(f"T'as pas eu ton bac, c'est bien dommage.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(97,100)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	if int(ctx.author.id)==XXXXXXX or int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(50,95)
		return await ctx.send(f"T'auras jamais ton bac bg je crois :/")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(97,100)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(90,100)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(1,1) else ' pas'}.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(75,100)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(1,2) else ' pas'}.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(97,100)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(95,100)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(1,1) else ' pas'}.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(95,100)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(87,100)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(1,1) else ' pas'}.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(99,105)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(0,5)
		return await ctx.send(f"Il y a {proba_bac}% de chance que t'es ton bac. Perso j'pense que tu l'auras{'' if avis_bac==randint(2,2) else ' pas'}.")
	if int(ctx.author.id)==XXXXXXX: 
		proba_bac=randint(97,100)
		return await ctx.send(f"T'as eu ton bac, félicitations à toi !")
	else:
		proba_bac=randint(0,100)
		return await ctx.send(f"Désolé bg mais j'te connais pas mais vu ta photo de profil et ton nom j'pense que t'as {proba_bac}% de chance d'avoir ton bac.")

@client.command(aliases=['inv', 'link'])
async def invitation(ctx):
	channel=client.get_channel(634054525312958464) #Salon #règles
	link=await channel.create_invite(unique=False, reason=f"créé par {ctx.author}")
	await ctx.send(f"**Lien d'invitation vers le serveur des ravaG :** {link}")

@client.command(aliases=['memo'])
async def note(ctx, *, text):
	if len(text)<=5:
		await ctx.send("Ta note doit au moins faire 5 caractères.")
	else:
		await ctx.channel.purge(limit=1)
		await ctx.author.send(f"** -- NOTE --**\n\n `{text}`")
		await ctx.send(f"Une note viens d'être envoyé à {ctx.author.name} !", delete_after=2)

@client.command(aliases=['hm'])
async def how_many(ctx):
	embed=discord.Embed(title=f"Listes users - Team ravaG", colour=discord.Colour.green())
	embed.set_footer(text=f"Développé par des ravaG.")
	listeusers(ctx)
	Lusers2=[]
	for member in Lusers:
		if member.status!=discord.Status.offline:
			Lusers2.append(member)
	embed.add_field(name="**Utilisateurs** - connectés/totaux", value=f"{len(Lusers2)}/{len(Lusers)}", inline=False)
	listeravaG(ctx)
	LravaG2=[]
	for member in LravaG:
		if member.status!=discord.Status.offline:
			LravaG2.append(member)
	embed.add_field(name="**ravaG** - connectés/totaux", value=f"{len(LravaG2)}/{len(LravaG)}", inline=False)
	listebot(ctx)
	Lbot2=[]
	for member in Lbot:
		if member.status!=discord.Status.offline:
			Lbot2.append(member)
	embed.add_field(name="**Bot** - connectés/totaux", value=f"{len(Lbot2)}/{len(Lbot)}", inline=False)
	listeverified(ctx)
	Lverified2=[]
	for member in Lverified:
		if member.status!=discord.Status.offline:
			Lverified2.append(member)
	embed.add_field(name="**Verified** - connectés/totaux", value=f"{len(Lverified2)}/{len(Lverified)}", inline=False)
	listeinvite(ctx)
	Linvite2=[]
	for member in Linvite:
		if member.status!=discord.Status.offline:
			Linvite2.append(member)
	embed.add_field(name="**Invités** - connectés/totaux", value=f"{len(Linvite2)}/{len(Linvite)}", inline=False)
	return await ctx.send(embed=embed)

@client.command()
async def syntax(ctx): #Meme commande que Sardbot
	syntaxe="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("```Js\n")
	syntaxe+=discord.utils.escape_markdown("//code en js (possible de remplacer 'js' par d'autres languages . adaptez le !)\n")
	syntaxe+=discord.utils.escape_markdown('console.log("hi");\n')
	syntaxe+=discord.utils.escape_markdown("```\n")
	syntaxe+="```Js\n"
	syntaxe+="//code en js (possible de remplacer 'js' par d'autres languages . adaptez le !)\n"
	syntaxe+='console.log("hi");\n'
	syntaxe+="```\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("`code sur une seule ligne`\n")
	syntaxe+="`code sur une seule ligne`\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("*texte en italique*\n")
	syntaxe+="*texte en italique*\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("**text en gras**\n")
	syntaxe+="**text en gras**\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("***text en italique-gras***\n")
	syntaxe+="***text en italique-gras***\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown("> cette ligne est cité\npas celle là\n")
	syntaxe+="> cette ligne est cité\npas celle là\n"
	syntaxe+="-----------------------------------------------------\n"
	syntaxe+=discord.utils.escape_markdown(">>> cette ligne est cité\ncelle là aussi (et elles le seront toutes!)\n")
	syntaxe+=">>> cette ligne est cité\ncelle là aussi (et elles le seront toutes!)\n"
	await ctx.send(syntaxe)

@client.command()
async def love(ctx, *users: discord.Member):
	if len(users)==2 or len(users)==1:
		UneDemande=False
		if len(users)==1:
			U=users
			users=[]
			users.append(U[0])
			users.append(ctx.author)
			UneDemande=True
		if users[0]==users[1]:
			return await ctx.send("Je suis sûr que cette personne s'aime ! :angry:")
		if users[0].nick:
			user1=list(users[0].nick)
		else:
			user1=list(users[0].name)
		if users[1].nick:
			user2=list(users[1].nick)
		else:
			user2=list(users[1].name)
		user1_CALC=retirerDoublons([x.lower() for x in user1])
		user2_CALC=retirerDoublons([x.lower() for x in user2])
		coef_amour=0
		if len(user1_CALC)>len(user2_CALC):
			taille_du_pls_grand=len(user1_CALC)
			taille_du_ms_grand=len(user2_CALC)
		else:
			taille_du_pls_grand=len(user2_CALC)
			taille_du_ms_grand=len(user1_CALC)
		coef_amour=round(float(len(list(set(user1_CALC).intersection(user2_CALC)))/taille_du_pls_grand),1)*100+((taille_du_pls_grand-taille_du_ms_grand)*1.5)*1.7
		if coef_amour>100:
			coef_amour=100
		if UneDemande==True:
			return await ctx.send(f"Tu as {coef_amour}% de chance de te mettre en couple avec {''.join(user1)}")
		await ctx.send(f"{''.join(user1)} et {''.join(user2)} ont {coef_amour}% de chance de se mettre en couple !")
	else:
		await ctx.send("Erreur! Syntaxe : `.love <User1> <User2>`")

def retirerDoublons(liste):
	Newliste=[]
	for element in liste:
		if element not in Newliste:
			Newliste.append(element)
	return Newliste

@love.error
async def love_error(ctx, error):
	await ctx.send(str(error).replace('Member "', "Le membre **").replace('" not found', "** n'as pas été trouvé."))

@client.command(aliases=['repost'])
async def delete(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		chiffre=randint(1,3)
		if chiffre==1:
			nom_fichier="delete.mp4"
		elif chiffre==2:
			nom_fichier="delete.mov"
		elif chiffre==3:
			nom_fichier="delete2.mp4"
		return await ctx.send(file=discord.File(f"files/{nom_fichier}"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command(aliases=['nul'])
async def nulle(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		chiffre=randint(1,5)
		if chiffre==1:
			nom_fichier="nulle.mp4"
		elif chiffre==2:
			nom_fichier="nulle.mov"
		elif chiffre==3:
			nom_fichier="nulle2.mp4"
		elif chiffre==4:
			nom_fichier="nulle3.mp4"
		elif chiffre==5:
			nom_fichier="nulle4.mp4"
		return await ctx.send(file=discord.File(f"files/{nom_fichier}"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command(aliases=['tg'])
async def tagueule(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		return await ctx.send(file=discord.File(f"files/tagueule.mp4"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command(aliases=['fdp'])
async def filsdepute(ctx, *, args=""): #neutre sert a rien, juste pour le .boulanger
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		if int(ctx.author.id)==XXXXX: #XXXXX correspond a un id de compte discord
			return await ctx.send("C'est toi le fils de pute")
		if args.casefold()=="Boulanger".casefold():
			chiffre=2
		else:
			chiffre=randint(1,2)
		return await ctx.send(file=discord.File(f"files/filsdepute{chiffre}.mp4"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command()
async def boulanger(ctx):
	await ctx.invoke(client.get_command("filsdepute"), args="Boulanger")

@client.command(aliases=['bin'])
async def binary(ctx, *, args):
	texte=str(args).encode()
	rendu=""
	for i in texte:
		rendu+=str(bin(i)[2:].zfill(8))
	await ctx.send(f"{rendu}")

@client.command(aliases=['cit'])
async def citation(ctx, msgID: discord.Message, *, args=""):
	embed=discord.Embed(icon_url=msgID.author.avatar_url, title=f"{msgID.author.name}#{msgID.author.discriminator} le {str(msgID.created_at)[8:10]}/{str(msgID.created_at)[5:7]}/{str(msgID.created_at)[:4]} à {str(msgID.created_at)[11:13]}:{str(msgID.created_at)[14:16]}", description=msgID.content, colour=discord.Colour.blue())
	embed.set_footer(text=f"Demandé par {ctx.author}")
	await ctx.channel.purge(limit=1)
	if len(msgID.content)<1:
		await ctx.send(f"Ce message n'est pas citable. Le lien du message : https://discordapp.com/channels/{msgID.guild.id}/{msgID.channel.id}/{msgID.id}")
	else:
		await ctx.send(embed=embed)
	if len(args)>1:
		await ctx.send(f"**Réponse de {ctx.author.mention} :**\n{args}")


@client.command(aliases=['bvn'])
async def bienvenue(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		return await ctx.send(f"**{ctx.author.mention} souhaite la bienvenue !!**", file=discord.File("files/welcome.mp4"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command()
async def vidage(ctx):
	if ctx.channel==client.get_channel(634059175004995587):
		messages=[]
		async for x in ctx.message.channel.history():
			if x.author==ctx.author:
				messages.append(x)
		await ctx.channel.delete_messages(messages)
		await ctx.send("Tous vos messages ont été supprimés.", delete_after=2)
		await ctx.send("Merci de ne pas abuser de cette commande.", delete_after=4)
	else:
		await ctx.send("Tu ne peux pas utiliser cette commande.")

@client.command()
async def runtime(ctx):
	now = datetime.datetime.now()
	elapsed = now - starttime
	seconds = elapsed.seconds
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	return await ctx.send(f"Lancé depuis {elapsed.days} jours, {hours}h {minutes}min {seconds}sec.")

@client.command()
async def ctsurenft(ctx):
	await ctx.invoke(client.get_command("memes"), args="ctsurenft")

@client.command()
async def xd(ctx):
	chiffre=randint(1,3)
	if chiffre==1:
		nom_fichier="XD.jpg"
	elif chiffre==2:
		nom_fichier="XD2.jpg"
	elif chiffre==3:
		nom_fichier="XD3.jpg"
	return await ctx.send("?XD", file=discord.File(f"files/{nom_fichier}"))

@client.command()
async def suceptible(ctx):
	return await ctx.send(file=discord.File(f"files/suceptible.mp4"))

@client.command()
async def troll(ctx):
	users=json.load(open('data/users.json', 'r'))
	try:
		dernier_message_temps=users[str(571348123855880192)]['dernier_message_XP_pics']
		dernier_message_temps=datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
		created_at=datetime.datetime.now()
		ecart=created_at-dernier_message_temps #caclul l'écart
	except:
		users[str(571348123855880192)]={}
		dernier_message_temps=users[str(571348123855880192)]['experience']=-1
		ecart=datetime.timedelta(seconds=6)
	if ecart.seconds>=5:
		users[str(571348123855880192)]['dernier_message_XP_pics']=datetime.datetime.now()
		json.dump(users, open('data/users.json', 'w'), default=JSONEncoder, indent=4, sort_keys=True)
		chiffre=randint(1,3)
		if chiffre==1:
			nom_fichier="Troll.png"
		elif chiffre==2:
			nom_fichier="Troll2.webp"
		elif chiffre==3:
			nom_fichier="Troll3.png"
		return await ctx.send(file=discord.File(f"files/{nom_fichier}"))
	else:
		t=5-ecart.seconds
		await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)

@client.command()
async def delchat(ctx, *, number: int):
	listeravaG(ctx)
	if ctx.author in LravaG:
		messages=[]
		async for x in ctx.message.channel.history(limit=number+1):
			messages.append(x)
		try:
			await ctx.channel.delete_messages(messages)
		except:
			return await ctx.send("Je ne peux pas supprimer les messages vieux de plus de 14 jours.")
		await ctx.send('Messages supprimés !', delete_after=4)
		await ctx.send("Merci de ne pas abuser de cette commande.", delete_after=4)
	else:
		await ctx.send("Tu ne peux pas faire ça.")

# Commande listes
def listeravaG(ctx):
	global LravaG
	LravaG=[]
	ravaG=discord.utils.get(ctx.guild.roles, name="😎 ravaG")
	for member in ctx.guild.members:
		if ravaG in member.roles:
			LravaG.append(member)

def listeverified(ctx):
	global Lverified
	Lverified=[]
	verified=discord.utils.get(ctx.guild.roles, name="🐾 Verified")
	for member in ctx.guild.members:
		if verified in member.roles:
			Lverified.append(member)

def listeinvite(ctx):
	global Linvite
	Linvite=[]
	invite=discord.utils.get(ctx.guild.roles, name="👤 Invité")
	for member in ctx.guild.members:
		if invite in member.roles:
			Linvite.append(member)

def listebot(ctx):
	global Lbot
	Lbot=[]
	bot=discord.utils.get(ctx.guild.roles, name="🤖 Bot")
	for member in ctx.guild.members:
		if bot in member.roles:
			Lbot.append(member)

def listeusers(ctx):
	global Lusers
	Lusers=[]
	for member in ctx.guild.members:
		Lusers.append(member)

def listeadminBot(ctx):
	global LadminBot
	LadminBot=[]
	adminBot=discord.utils.get(ctx.guild.roles, name="admin-bot")
	for member in ctx.guild.members:
		if adminBot in member.roles:
			LadminBot.append(member)

def listechannel(ctx):
	global LchannelID
	LchannelID=[]
	try:
		for channel in ctx.guild.channels:
			LchannelID.append(channel.id)
	except AttributeError:
		pass

temps_lantence_avant=int(time.strftime("%S"))-1

client.run(token)