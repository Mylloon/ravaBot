import discord
from discord.ext import commands

import praw
import random
import urllib.request as request
import os
import json
import time
import datetime

class Meme(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def JSONEncoder(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

    @commands.command(name='memes', aliases=['meme'])
    async def memes_(self, ctx, *, args=""):
        users=json.load(open('data/users.json', 'r'))
        try:
            dernier_message_temps = users[str(571348123855880192)]['dernier_message_XP_pics']
            dernier_message_temps = datetime.datetime.strptime(dernier_message_temps, '%Y-%m-%dT%H:%M:%S.%f')
            created_at = datetime.datetime.now()
            ecart = created_at-dernier_message_temps #caclul l'écart
        except:
            users[str(571348123855880192)] = {}
            dernier_message_temps = users[str(571348123855880192)]['experience']=-1
            client = commands.Bot(command_prefix=".")
            ravaBot = await client.fetch_user(571348123855880192)
            dernier_message_temps = users[str(571348123855880192)]['nom_usuel']=f"{ravaBot.name}#{ravaBot.discriminator}"
            ecart = datetime.timedelta(seconds=6)
        if ecart.seconds >= 5:
            users[str(571348123855880192)]['dernier_message_XP_pics'] = datetime.datetime.now()
            json.dump(users, open('data/users.json', 'w'), default=self.JSONEncoder, indent=4, sort_keys=True)
            try:
                reddit = praw.Reddit(client_id='TON ID CLIENT', client_secret='TON CLIENT SECRET', user_agent='disreddit /u/xxxxxx, http://localhost:8080')

                if args == "ctsurenft": # si user demande meme 'ctsurenft'
                    subredditchoix = 'Meme de qualité'
                    image_meme = 'https://twitter.com/i/status/1181338160741191682'
                    return await ctx.send(f"**{subredditchoix}**: {image_meme}") #en attendant que discord fix les vidéos dans les embed

                elif args != "": # si il y a un arg différent d'un meme
                    subredditchoix = args

                else: # si il n'y a pas d'arguments
                    subredditchoix = random.choice(['memes','anime_irl','Animemes','BikiniBottomTwitter','dankmemes','DeepFriedMemes',
                    'educationalmemes','funny','marvelmemes','me_irl','meme','MemeEconomy','Memes_Of_The_Dank','MinecraftMemes',
                    'PewdiepieSubmissions','physicsmemes','reactiongifs','wholesomememes','blackpeopletwitter','metal_me_irl','bee_irl','coaxedintoasnafu','195',
                    'shittyadviceanimals','meirl','2meirl4meirl','AdviceAnimals','weirdmemes'])

                memes_submissions = reddit.subreddit(subredditchoix).hot()
                post_to_pick = random.randint(1, 10)
                for i in range(0, post_to_pick): # i pas important
                    submission = next(x for x in memes_submissions if not x.stickied)

                image_meme = submission.url
                subredditchoix = f"r/{subredditchoix}"

                embed = discord.Embed(title=f"{subredditchoix} pour {ctx.author.name}", colour=discord.Colour.green())
                embed.set_footer(text=f"Memes from reddit | Développé par des ravaG.")
                embed.set_image(url=image_meme)
                return await ctx.send(embed=embed)

            except Exception as error:
                print(f"args: {args}, subreddit: {subredditchoix}, error: {error}")
                return await ctx.send(f"Ce subreddit est interdit, mis en quarantaine ou n'existe pas. ({subredditchoix})")
        else:
            t = 5-ecart.seconds
            await ctx.send(f"Tu dois encore attendre {t} seconde{'s' if t>1 else ''} avant de lancer cette commande.", delete_after=2)


def setup(bot):
    bot.add_cog(Meme(bot))
