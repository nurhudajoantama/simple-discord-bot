import discord
from discord.ext import commands
import asyncio


class GeneralCommands(commands.Cog, name='General'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='This command returns the latency')
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** Latency: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='halo', help='This command returns the Halo quote')
    async def halo(self, ctx):
        await ctx.send(f'_Hola_!!, {ctx.message.author.name}')

    @commands.command(name='brutal', help='This spam with brutall messages | [n times int] [delay s float] [msg]')
    async def brutal(self, ctx, n, delay, *msgs):
        msg = ' '.join(msgs)
        for _ in range(int(n)):
            await ctx.send(msg)
            await asyncio.sleep(float(delay))

    @commands.command(name='author', help='This command returns the author of the bot')
    async def author(self, ctx):
        emded = discord.Embed(
            title='Author',
            description=f'This bot is created by **nurhudajoantama**',
            color=0x003366
        )
        await ctx.send(embed=emded)

    @commands.command(name='profile', help='This command returns the profile of the user you mention')
    async def profile(self, ctx):
        user = ctx.message.mentions[0]
        emded = discord.Embed(
            title='Profile',
            description=f'{user.mention}',
            color=0x003366
        )
        emded.add_field(name='Display Name',
                        value=user.display_name, inline=False)
        emded.add_field(name='Name', value=user.name, inline=False)
        emded.add_field(name='Status', value=user.status, inline=False)

        emded.set_image(url=user.avatar_url)
        await ctx.send(embed=emded)
