from client import Client
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
    bot.add_cog(Music(bot))
    bot.add_cog(GeneralCommands(bot))
    bot.run(os.getenv('DC_TOKEN'))


if __name__ == '__main__':
    main()
