import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
import lyricsgenius

genius = lyricsgenius.Genius("TON TOKEN GENIUS")

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # Les adresses ipv6 posent parfois des problèmes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class VoiceConnectionError(commands.CommandError):
    """Classe d'exception personnalisée pour les erreurs de connexion."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception pour les cas de canaux vocaux non valables."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) ont d'autres informations utiles que vous pourriez vouloir
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Nous permet d'accéder à des attributs similaires à un dict.
        Cette fonction n'est utile que lorsque vous n'êtes pas en train de télécharger.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=True):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # prendre le premier élément d'une liste de lecture
            data = data['entries'][0]

        await ctx.send(f'```ini\n[{data["title"]} ajouté à la queue.]\n```')

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Utilisé pour préparer un flux, au lieu de le télécharger.
        Depuis l'expiration des liens de streaming Youtube."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=True)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)

class MusicPlayer:
    """Une classe qui est attribuée à chaque guilde à l'aide du bot pour la musique.
    Cette classe met en place une file d'attente et une boucle, ce qui permet aux différentes guildes d'écouter différentes listes de lecture
    simultanément.
    Lorsque le bot se déconnecte de la Voix, son instance est détruite.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Message en cours de lecture
        self.volume = .4 # Volume défini initalement (.5 = 50%)
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Player loop principale"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Attendez la prochaine chanson. Si nous annulons le lecteur et le déconnecter...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # La source était probablement un flux (non téléchargé)
                # Nous devrions donc nous regather pour éviter l'expiration des flux
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'Il y a eu une erreur dans le traitement de votre chanson.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Joue :** `{source.title}` demandé par '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Veillez à ce que le processus FFmpeg soit clean.
            source.cleanup()
            self.current = None

            try:
                # Nous ne jouons plus cette chanson...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Déconnecte et nettoie le lecteur."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Commandes liées à la musique."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """Un contrôle local qui s'applique à tous les commandements de ce cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """Un gestionnaire d'erreur local pour toutes les erreurs découlant des commandes de ce rouage."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('Cette commande ne peut pas être utilisée dans les messages privés.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Erreur de connexion au canal vocal. '
                           'Veuillez vous assurer que vous êtes dans un channel valide ou alors en spécifier un.')

        print('Ignorer l''exception dans la commannde {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Récupérer le joueur du serveur, ou en générer un."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Se connecte au vocal.
        Paramètres
        ------------
        channel: discord.VoiceChannel [Optionnel]
            Le channel auquel il faut se connecter. Si un channel n'est pas spécifié, une tentative de rejoindre le canal vocal dans lequel vous êtes
            sera faite.
        Cette commande gère également le déplacement du bot vers différents channel.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send('Pas de channel à rejoindre. Veuillez soit spécifier un channel valide, soit en rejoindre un.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                return await ctx.send(f'Move vers le channel : <{channel}> a expiré.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                return await ctx.send(f'Connexion au channel : <{channel}> a expiré.')

        await ctx.send(f'Connexion à : **{channel}**')

    @commands.command(name='play', aliases=['p'])
    async def play_(self, ctx, *, search: str):
        """Demandez une chanson et ajoutez-la à la liste d'attente.
        Cette commande tente de rejoindre un canal vocal valide si le bot n'en fait pas déjà partie.
        Utilise YTDL pour rechercher et récupérer automatiquement une chanson.
        Paramètres
        ------------
        search: str [Required]
            La chanson à rechercher et à récupérer en utilisant YTDL. Il peut s'agir d'une simple recherche, d'une ID ou d'une URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # Si le téléchargement est sur False, la source sera un dict qui sera utilisé plus tard pour reconstituer le flux.
        # Si le téléchargement est sur True, la source sera un discord.FFmpegPCMAudio avec un VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=True)

        await player.queue.put(source)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Met en pause la chanson en cours de lecture."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('Je ne joue rien en ce moment !')
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Pause de la chanson !')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Reprend la chanson actuellement en pause."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne joue rien en ce moment !')
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Reprenez la chanson !')

    @commands.command(name='skip', aliases=['s'])
    async def skip_(self, ctx):
        """Skip la chanson."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne joue rien en ce moment !')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skip la chanson !')

    @commands.command(name='queue', aliases=['q'])
    async def queue_info(self, ctx):
        """Affiche la playlist de musiques à venir."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne suis pas connecté au channel vocal actuellement !')

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('Il n''y a actuellement plus de chansons en attente.')

        # Saisissez jusqu'à 5 entrées dans la file d'attente...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f"Prochainement - {len(upcoming)} restant{'s' if len(upcoming)>1 else ''}", description=fmt)

        await ctx.send(embed=embed)

    @commands.command(name='now_playing', aliases=['np'])
    async def now_playing_(self, ctx):
        """Affiche des informations sur la chanson en cours de lecture."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne suis pas connecté au channel vocal actuellement !')

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('Je ne joue rien en ce moment !')

        try:
            # Supprimez notre message "now_playing" précédent.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'**Joue :** `{vc.source.title}` '
                                   f'demandé par `{vc.source.requester}`')

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Changez le volume du lecteur.
        Paramètres
        ------------
        volume: float or int [Required]
            Le volume à régler en pourcentage du lecteur. Celui-ci doit être compris entre 1 et 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne suis pas connecté au channel vocal actuellement !')

        if not 0 < vol < 101:
            return await ctx.send('Veuillez saisir une valeur comprise entre 1 et 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: Volume réglé sur **{vol}%**')

    @commands.command(name='disconnect', aliases=['dc','stop'])
    async def disconnect_(self, ctx):
        """Arrêtez la chanson en cours de lecture et détruisez le lecteur.
        !Avertissement!
            Cela détruira le joueur affecté au serveur, en supprimant également les chansons et les paramètres en attente (c'est généralement ce qu'on veut faire).
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Je ne joue rien en ce moment !')

        await self.cleanup(ctx.guild)
        await ctx.send(f'Déconnexion.')

    @commands.command(name='lyrics', aliases=['l', 'lyric']) #caractere vide: \u200b
    async def lyrics_(self, ctx, *, song: str=None):
        vc=ctx.voice_client
        player=self.get_player(ctx)
        if song or player.current:
            if not song:
                song=f"{vc.source.title}"
            await ctx.send(f":mag: Cherche les paroles pour `{song}`")
            song=genius.search_song(song)
            couleur_embed=0xD3D3D3
            try:
                paroles=str(song.lyrics)
            except:
                return await ctx.send(f"Pas de résultats trouvés pour : `{vc.source.title}`")
            lignetotal=""
            premierembed=True
            if len(paroles)>7500:
                return await ctx.send("Désolé, les paroles sont trop longues pour être affichés.")
            for ligne in paroles.split("\n"):
                if len(f"{lignetotal}\n{ligne}")<1024:
                    lignetotal=f"{lignetotal}\n{ligne}"
                else:
                    if premierembed==True:
                        premierembed=False
                        embed=discord.Embed(title=f'Paroles de {(str(song).split(":"))[0].replace("by", "par")}.', description=lignetotal, color=couleur_embed)
                    else:
                        embed=discord.Embed(description=lignetotal, color=couleur_embed)
                    await ctx.send(embed=embed)
                    lignetotal=f"{ligne}"
            if premierembed==True:
                premierembed=False
                embed=discord.Embed(description=lignetotal, color=couleur_embed)
            else:
                embed=discord.Embed(description=lignetotal, color=couleur_embed)
            embed.set_footer(icon_url=ctx.author.avatar_url,text=f"Demandé par {ctx.author} | Lyrics de RapGenius")
            return await ctx.send(embed=embed)
        else:
            await ctx.send("Aucune musique demandé... `.lyrics <song>`")

def setup(bot):
    bot.add_cog(Music(bot))
