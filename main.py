import logging
import sys

import discord
from discord.ext.commands import Bot

from settings import discord as discord_settings
from utils import utils

# Set up logging
logging.basicConfig(filename='movie_bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Set up bot instance
bot = Bot(command_prefix=discord_settings.bot_prefix)

# Command groups to add
cogs = ['cogs.user_commands',
        'cogs.movie_commands',
        'cogs.poll_commands']

# Global variable to hold the server's channel where this bot should post messages to
send_to_channel = None

# Global variable to hold the server's channel where this bot should read messages from
read_from_channel = None

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    # Set the bot's activity to playing Matchmaker
    await bot.change_presence(activity=discord.Game(name="Automated Movie Curator"))

    # Set the channel on the server which the bot post messages to
    global send_to_channel
    send_to_channel = bot.get_channel(discord_settings.send_to_channel)

    # Set the channel on the server which the bot reads messages from
    global read_from_channel
    read_from_channel = bot.get_channel(discord_settings.read_from_channel)

    for cog in cogs:
        logging.info(f"Loaded commands from {cog}")
        bot.load_extension(cog)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        msg = f'Bot start up.  Running main() AMC'
        utils.print_and_log(msg)
        bot.run(discord_settings.token)
    else:
        msg = f'Bot not running.  In console mode'
        utils.print_and_log(msg)
