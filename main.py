import discord
from client import Client
from custom_commands import CustomCommands
from general_commands import GeneralCommands
from gundar_info_commands import GundarInfoCommands
from music import Music
import os
from dotenv import load_dotenv
load_dotenv()


def main():

    DC_TOKEN = os.getenv('DC_TOKEN')
    DATABASE_FILE = 'db/database.db'
    c_prefix = 'n!'
    ENV = os.getenv('ENV')
    if ENV == 'prod':
        DC_TOKEN = os.getenv('DC_TOKEN')
    elif ENV == 'dev':
        DC_TOKEN = os.getenv('DEV_DC_TOKEN')
        c_prefix = 'dn!'

    if not os.path.exists('db'):
        os.makedirs('db')
    if not os.path.exists(DATABASE_FILE):
        print('Creating database file...')
        open(DATABASE_FILE, 'a').close()

    intents = discord.Intents.default()
    intents.members = True

    bot = Client(
        command_prefix=c_prefix,
        intents=intents
    )
    bot.add_cog(GeneralCommands(bot))
    bot.add_cog(CustomCommands(bot, DATABASE_FILE))
    bot.add_cog(GundarInfoCommands(bot))
    bot.add_cog(Music(bot))
    bot.run(DC_TOKEN)


if __name__ == '__main__':
    main()
