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


class Music(commands.Cog, name='Music module'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='This command makes the bot join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            channel = ctx.message.author.voice.channel

        await channel.connect()

    @commands.command(name='leave', help='This command stops the music and makes the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()

    @commands.command(name='loop', help='This command toggles loop mode')
    async def loop_(self, ctx):
        global loop

        if loop:
            await ctx.send('Loop mode is now `False!`')
            loop = False

        else:
            await ctx.send('Loop mode is now `True!`')
            loop = True

    @commands.command(name='play', help='This command plays music')
    async def play(self, ctx):
        # global queue
        guild_id = str(ctx.message.guild.id)

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        elif len(queue.get(guild_id)) == 0:
            await ctx.send('Nothing in your queue! Use `?queue` to add a song!')

        else:
            try:
                channel = ctx.message.author.voice.channel
                await channel.connect()
            except:
                pass

        server = ctx.message.guild
        voice_channel = server.voice_client
        while len(queue.get(guild_id)) != 0:
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

                await ctx.send('**Now playing:** {}'.format(player.title))

            except Exception as e:
                print(e)
                break

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        voice_channel = ctx.message.guild.voice_client
        voice_channel.stop()
        voice_channel.resume()

    @commands.command(name='volume', help='This command changes the bots volume')
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        print(ctx.voice_client)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()

    @commands.command(name='resume', help='This command resumes the song!')
    async def resume(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()

    @commands.command(name='stop', help='This command stops the song!')
    async def stop(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.stop()

    @commands.command(name='queue')
    async def queue_(self, ctx, *, url):
        # global queue
        guild_id = str(ctx.message.guild.id)
        q = queue.get(guild_id)
        q.append(url)
        queue.set(guild_id, q)
        await ctx.send(f'`{url}` added to queue!')

    @commands.command(name='remove')
    async def remove(self, ctx, number):
        # global queue
        guild_id = str(ctx.message.guild.id)
        q = queue.get(guild_id)

        try:
            del(q[int(number)])
            queue.set(guild_id, q)
            await ctx.send(f'Your queue is now `{q}!`')

        except:
            await ctx.send('Your queue is either **empty** or the index is **out of range**')

    @commands.command(name='view', help='This command shows the queue')
    async def view(self, ctx):
        q = queue.get(str(ctx.message.guild.id))
        if q is None:
            await ctx.send('Your queue is **empty**')
        else:
            await ctx.send(f'Your queue is `{q}`')
