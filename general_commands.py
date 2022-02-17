import discord
from discord.ext import commands


class GeneralCommands(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='This command returns the latency')
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** Latency: {round(self.bot.latency * 1000)}ms')
