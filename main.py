from client import Client
from custom_commands import CustomCommands
from general_commands import GeneralCommands
from music import Music
import os
from dotenv import load_dotenv
load_dotenv()


def main():
    """
    Main function
    """
    bot = Client(
        command_prefix='n!'
    )
    bot.add_cog(GeneralCommands(bot))
    bot.add_cog(CustomCommands(bot, os.getenv('DB_URI')))
    bot.add_cog(Music(bot))
    bot.run(os.getenv('DC_TOKEN'))


if __name__ == '__main__':
    main()
