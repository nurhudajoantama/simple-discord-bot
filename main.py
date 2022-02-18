import discord
from client import Client
from custom_commands import CustomCommands, Database
from db_pool import DatabasePool
from general_commands import GeneralCommands
from gundar_info_commands import GundarInfoCommands
from music import Music
import psycopg2.pool
import os
from dotenv import load_dotenv
load_dotenv()


def main():

    DC_TOKEN = os.getenv('DC_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')
    c_prefix = 'n!'
    ENV = os.getenv('ENV')
    if ENV == 'prod':
        DC_TOKEN = os.getenv('DC_TOKEN')
    elif ENV == 'dev':
        DC_TOKEN = os.getenv('DEV_DC_TOKEN')
        DATABASE_URL = os.getenv('DEV_DATABASE_URL')
        c_prefix = 'dn!'

    intents = discord.Intents.default()
    intents.members = True

    db_pool = DatabasePool(DATABASE_URL)

    bot = Client(
        command_prefix=c_prefix,
        intents=intents
    )
    bot.add_cog(GeneralCommands(bot))
    bot.add_cog(CustomCommands(bot, db_pool))
    bot.add_cog(GundarInfoCommands(bot))
    bot.add_cog(Music(bot))
    bot.run(DC_TOKEN)


if __name__ == '__main__':
    main()
