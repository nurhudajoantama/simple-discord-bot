import discord
from discord.ext import commands


class GeneralCommands(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='This command returns the latency')
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** Latency: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='halo', help='This command returns the Halo quote')
    async def halo(self, ctx):
        await ctx.send(f'_Hola_!!, {ctx.message.author.name}')

    @commands.command(name='author', help='This command returns the author of the bot')
    async def author(self, ctx):
        author = self.bot.get_user(497765332149207043)
        emded = discord.Embed(
            title='Author',
            description=f'This bot is created by **{author.mention}**',
            color=0x00ff00
        )
        emded.set_thumbnail(url=author.avatar_url)
        await ctx.send(embed=emded)
