import discord
from discord.ext import commands, tasks


class Client(commands.Bot):

    async def on_ready(self):
        await self.change_status()
        print('Bot is online!')

    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, name='general')
        await channel.send(f'Welcome {member.mention}! See `n!help` command for details!')

    async def change_status(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="n!help"))
