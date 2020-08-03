import discord
from discord.ext import commands

import random
import requests
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from googleapiclient.discovery import build

class Nsfw(commands.Cog):

    # Init

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    # Research

    def _get_lewd_image(self, what):
        api_url = f"http://api.o{what}.ru/noise/"

        r = requests.get(api_url)
        response = r.json()
        preview = response[0]['preview']
        r.close()

        image_url = f"http://media.o{what}.ru/{preview}"
        return image_url

    # Commands

    @commands.command(aliases=['sexes','nude','nudes'])
    async def sexe(self, ctx, *, choice_of_nsfw=None):
        liste_hot=['butts', 'boobs']
        if choice_of_nsfw in liste_hot:
            pass
        else:
            choice_of_nsfw = random.choice(liste_hot)
        if ctx.channel.is_nsfw():
            lewd_image = self._get_lewd_image(choice_of_nsfw)
            #await ctx.send(lewd_image)
            embed=discord.Embed(title=f"{choice_of_nsfw.capitalize()} pour {ctx.author.name}", colour=discord.Colour.purple())
            embed.set_footer(text=f"Développé par des ravaG.")
            embed.set_image(url=lewd_image)
            await ctx.send(embed=embed)
        else:
            nsfw_channel = self.bot.get_channel(594713819167588387)
            await ctx.send(f"Désolé mais je n'envois ce genre de message seulement dans {nsfw_channel.mention} !", delete_after=2)

    # En cas d'erreur

    @sexe.error
    async def sexe_error(self, ctx, error):
        await ctx.send("Une erreur est survenu lors du traitement de votre commande, veuillez réessayez !", delete_after=2)

def setup(bot):
    bot.add_cog(Nsfw(bot))
