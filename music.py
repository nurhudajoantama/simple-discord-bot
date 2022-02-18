import discord
from discord.ext import commands
import asyncio
import youtube_dl


class Queue():
    def __init__(self):
        self.queue = {}

    def get(self, server):
        if server in self.queue:
            return self.queue[server]
        else:
            return []

    def set(self, server, songs):
        self.queue[server] = songs

    def remove(self, server):
        if server in self.queue:
            del self.queue[server]


queue = Queue()

loop = False

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


wait_until_leave = 60  # in seconds


class Music(commands.Cog, name='Music module'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mjoin', help='This command makes the bot join the voice channel')
    async def mjoin(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()

            voice_channel = ctx.message.guild.voice_client
            # If it's not playing it waits
            await asyncio.sleep(wait_until_leave)
            while voice_channel.is_playing():  # and checks once again if the bot is not playing
                break  # if it's playing it breaks
            else:
                await voice_channel.disconnect()  # if not it disconnects
                await ctx.send('**Music ended**, Nothing is playing now, _I am leave_')

    @commands.command(name='mleave', help='This command stops the music and makes the bot leave the voice channel')
    async def mleave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        queue.remove(str(ctx.message.guild.id))
        await voice_client.disconnect()

    @commands.command(name='mloop', help='This command toggles loop mode')
    async def mloop_(self, ctx):
        global loop

        if loop:
            await ctx.send('Loop mode is now `False!`')
            loop = False

        else:
            await ctx.send('Loop mode is now `True!`')
            loop = True

    @commands.command(name='mp', help='This command plays music')
    async def mp(self, ctx, *, url):
        # global queue
        guild_id = str(ctx.message.guild.id)

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            q = queue.get(guild_id)
            q.append(url)
            queue.set(guild_id, q)
            await ctx.send(f'`{url}` added to queue!')

            try:
                channel = ctx.message.author.voice.channel
                await channel.connect()
            except:
                pass

        server = ctx.message.guild
        voice_channel = server.voice_client
        if (voice_channel.is_playing() or voice_channel.is_paused()) and len(queue.get(guild_id)) > 1:
            return
        while queue.get(guild_id):
            try:
                while voice_channel.is_playing() or voice_channel.is_paused():
                    await asyncio.sleep(2)
                    pass

            except AttributeError:
                pass

            try:
                async with ctx.typing():
                    player = await YTDLSource.from_url(queue.get(guild_id)[0], loop=self.bot.loop)
                    voice_channel.play(player, after=lambda e: print(
                        'Player error: %s' % e) if e else None)

                    q = queue.get(guild_id)
                    if loop:
                        q.append(queue[0])
                    del(q[0])
                    queue.set(guild_id, q)

                await ctx.send(f'**Now playing:** {player.data["title"]} | {player.data["channel"]}')

            except Exception as e:
                print(e)
                break

        while voice_channel.is_playing():  # Checks if voice_channel is playing
            await asyncio.sleep(1)  # While it's playing it sleeps for 1 second
        else:
            # If it's not playing it waits
            await asyncio.sleep(wait_until_leave)
            while voice_channel.is_playing():  # and checks once again if the bot is not playing
                break  # if it's playing it breaks
            else:
                await voice_channel.disconnect()  # if not it disconnects
                await ctx.send('**Music ended**, Nothing is playing now, _I am leave_')

    @commands.command(name='mskip', help='Skips the current song')
    async def mskip(self, ctx):
        voice_channel = ctx.message.guild.voice_client
        voice_channel.stop()
        voice_channel.resume()

    @commands.command(name='mvolume', help='This command changes the bots volume')
    async def mvolume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        print(ctx.voice_client)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(name='mpause', help='This command pauses the song')
    async def mpause(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()

    @commands.command(name='mresume', help='This command resumes the song!')
    async def mresume(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()

    @commands.command(name='mstop', help='This command stops the song!')
    async def mstop(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.stop()

    @commands.command(name='mqueue', help="This command shows the queue")
    async def mqueue_(self, ctx):
        q = queue.get(str(ctx.message.guild.id))
        if len(q) == 0:
            await ctx.send('Your queue is **empty**')
        else:
            lmusic = '**List of songs in queue:**\n'
            for i, m in enumerate(q):
                lmusic += f'{str(i+1)}. {str(m)}\n'
            await ctx.send(lmusic)

    @commands.command(name='mrmv', help="This command removes a song from the queue")
    async def mremove(self, ctx, number):
        number = int(number) - 1
        if number < 0:
            await ctx.send('the index is **out of range**')
            return

        guild_id = str(ctx.message.guild.id)
        q = queue.get(guild_id)

        try:
            del(q[number])
            queue.set(guild_id, q)
            if len(q) == 0:
                await ctx.send('Your queue is now **empty**')
            else:
                lmusic = 'List of songs in queue:\n'
                for i, m in enumerate(q):
                    lmusic += f'{str(i+1)}. {str(m)}\n'

                await ctx.send(f'Your queue is\n`{lmusic}`')

        except:
            await ctx.send('Your queue is either **empty** or the index is **out of range**')
