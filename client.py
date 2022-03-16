import discord
from discord.ext import commands, tasks


class Client(commands.Bot):

    async def on_ready(self):
        await self.change_status()
        print('Bot is online!')

    async def on_message(self, message):
        if self.user == message.author:
            return
        else:
            await self.process_commands(message)

    async def change_status(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="n!help"))
