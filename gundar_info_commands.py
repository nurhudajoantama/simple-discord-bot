import discord
from discord.ext import commands
import requests


def format_embed(n):
    embed = discord.Embed(
        title=n['title'],
        url=n['url'],
        description=n['content'],
        author=n['user'],
    )
    embed.add_field(name='date', value=n['date'])
    return embed


class GundarInfoCommands(commands.Cog, name='Gundar info'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ginfoss', help='Show u gundar info in student site')
    async def ginfoss(self, ctx):
        r = requests.get('http://oldsite.gunadarma.ac.id/apiweb/ss').json()

        for n in r["ss"]:
            embed = format_embed(n)
            await ctx.send(embed=embed)

    @commands.command(name='ginfobaak', help='Show u gundar info in BAAK')
    async def ginfobaak(self, ctx):
        r = requests.get('http://oldsite.gunadarma.ac.id/apiweb/baak').json()

        for n in r["baak"]:
            embed = format_embed(n)
            await ctx.send(embed=embed)

    @commands.command(name='ginfo', help='Show u gundar info news')
    async def ginfo(self, ctx):
        r = requests.get('http://oldsite.gunadarma.ac.id/apiweb/news').json()

        for n in r["news"]:
            n['url'] = 'https://gunadarma.ac.id/rnd/' + n['url']
            embed = format_embed(n)
            await ctx.send(embed=embed)

    @commands.command(name='ginfobidkem', help='Show u gundar info in bidkem')
    async def ginfobidkem(self, ctx):
        r = requests.get('http://oldsite.gunadarma.ac.id/apiweb/bidkem').json()

        for n in r["bidkem"]:
            embed = format_embed(n)
            await ctx.send(embed=embed)
