import discord
from discord.ext import commands
import sys
import asyncio
from token_and_api_key import *
from parsing_utils import recent_games_parser
import time

initial_extensions = (
    'cogs.stats',
    'cogs.pro',
    'cogs.meta',
    'cogs.pics',
    'cogs.voice',
    'cogs.game'
    )
help_attrs = dict(hidden=True)
description = '''Hey! I'm a bot that provides some Dota2 related utilities.'''
bot = commands.Bot(
    command_prefix='!',
    description=description,
    pm_help=False,
    help_attrs=help_attrs
    )


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.bot:
        return

    await bot.process_commands(message)




@bot.event
async def auto_parsing():
    channel = discord.Object(id=log_chat_id)
    await bot.wait_until_ready()
    while not bot.is_closed:
        for player_id in array_of_ids:
            reply = recent_games_parser.get_recent_matches(player_id)

            await bot.send_message(channel, reply)

        await asyncio.sleep(60*60)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = int(time.time())

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    launch_time = int(time.time())
    #bot.loop.create_task(auto_parsing())
    bot.run(token)
