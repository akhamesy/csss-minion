# py -m pip install -U __
# pylint: disable=C
import discord
import os
from discord.ext import commands
import configparser
import getpass
import psycopg2
import urllib.parse
import random
import asyncio
import codecs as codex
import math
import time
import subprocess
import sys
from io import StringIO
import logging
from pagination import Pages

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

log_file = open('discord.log', 'a', 1)
sys.stdout = log_file
sys.stderr = log_file

f = open('discord.log', 'r')
f.seek(0)
configFile = "botMain.settings"

#check if config file exists, if not, input manually
if not os.path.isfile(configFile):
    DISCORD_API_ID = getpass.getpass('Discord API: ')
    token = getpass.getpass('Token: ')
    wolframid = getpass.getpass('Wolframalpha: ')
    ip = "172.93.48.238:25565"
    description = "Bot of the CSSS"
    postgrespass = getpass.getpass('Database Password: ')
    mashape_key = getpass.getpass('Mashape Key: ')
    local_postgres_pw = getpass.getpass('Database Password: ')
    imgur_id = getpass.getpass('Imgur client id: ')
else:
    #Load the config file
    config = configparser.ConfigParser()
    config.read(configFile)
    description = config.get("Discord", "Description")
    wolframid = config.get("Wolfram", "TokenId")
    DISCORD_API_ID = config.get("Discord", "API_ID")
    token = config.get("Discord", "Token")
    ip = "172.93.48.238:25565"
    postgrespass = config.get("Postgres", "Password")
    mashape_key = config.get("Mashape", "Token")
    local_postgres_pw = config.get("LocalPG", 'Password')
    imgur_id = config.get("Imgur", "client_id")

startup_extensions = ["levels", "classes", "misc", "info", "spellcheck", "poem", "dictionary", "wiki", "roullette", "urbandict", "youtubesearch", "duck","tunes", "imgur", "memes","sfusearch", "outlines", "roads", "announce","translate", "remindme", "modtools"]

bot = commands.Bot(command_prefix='.', description=description)
bot.wolframid = wolframid
bot.mcip = ip
bot.remove_command("help")
bot.mashape_key = mashape_key
bot.imgur_id = imgur_id
bot.lang_url = config.get("Translate","url")
bot.postgrespass = postgrespass

def reloadConfig():
    pass

bot.conn_wc = psycopg2.connect("port='5432' user='csss_minion' host='localhost' password='"+local_postgres_pw+"'") # second connection for wordcloud cog

@bot.event
async def on_ready():
    logger.warning('Logged in as')
    logger.warning(bot.user.name)
    logger.warning('------')
    await bot.change_presence(game=discord.Game(name='Yes my master'))

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command(pass_context = True)
async def load(ctx, name):
    if Henry(ctx):
        try:
            bot.load_extension(name)
        except(AttributeError, ImportError) as e:
            await bot.say("Cog load failed: {}, {}".format(type(e), str(e)))
            return
        await bot.say("{} cog loaded.".format(name))
    else:
        await bot.say("You ain't my master! Shoo!")

@bot.command(pass_context = True)
async def unload(ctx, name):
    if Henry(ctx):
        bot.unload_extension(name)
        await bot.say("{} cog unloaded".format(name))
    else:
        await bot.say("You ain't my master! Shoo!")

@bot.command(pass_context = True)
async def reload(ctx, name):
    if Henry(ctx):
        bot.unload_extension(name)
        try:
            bot.load_extension(name)
        except(AttributeError, ImportError) as e:
            await bot.say("Cog load failed: {}, {}".format(type(e), str(e)))
            return
        await bot.say("`{} cog reloaded`".format(name))
    else:
        await bot.say("`You ain't my master! Shoo!``")

@bot.command(pass_context = True)
async def exc(ctx, *args):
    if Henry(ctx):
        query = " ".join(args)
        await bot.say("```"+subprocess.getoutput(query)+"```")
    else:
        await bot.say("You ain't my master! Shoo!")

def Henry(ctx):
    if ctx.message.author.id == "173702138122338305":
        return True
    else:
        return False

async def embed_this_for_me(text, ctx):
    """Standardized embeddings across cogs"""
    callingframe = sys._getframe(1)
    em = discord.Embed(colour=0xfff)
    em.add_field(name="Results from "+callingframe.f_code.co_name, value=text)
    #em.set_footer(text="Written by Nos", icon_url="https://cdn.discordapp.com/avatars/173177975045488640/61d53ada7449ce4a3e1fdc13dc0ee21e.png")
    await bot.send_message(ctx.message.channel, embed=em)

def fit_msg(msg, maxlen:int=2000):
    """Split a long message to fit within discord's limits.
            Uses the following order of division for natural splits:
            newline > space > any char
        """
    msgs = []

    while len(msg) >= maxlen:
        if '\n' in msg[:maxlen]:
            idx = msg[:maxlen].rfind('\n') #find last occurance of newline
            msgs.append(msg[:idx])
            msg = msg[idx+1:] #careful which side gets the newline

        elif ' ' in msg[:maxlen]:
            idx = msg[:maxlen].rfind(' ')
            msgs.append(msg[:idx])
            msg = msg[idx+1:]

        else:
            for x in range(maxlen,0,-1):
                msgs.append(msg[:x])
                msg = msg[x:]
                break;

    msgs.append(msg)
    return msgs

# testing if the bot is alive
@bot.command()
async def ping():
    await bot.say("pong")

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logger.warning('Failed to load extension {}\n{}'.format(extension, exc))

@bot.command(pass_context=True)
async def cogs(ctx):
    """Lists the currently loaded cogs."""
    cogs = list(bot.cogs.keys())
    cogs.sort()
    await bot.embed_this_for_me("\n".join(cogs), ctx)

# used to update the queue
async def update():
  await bot.wait_until_ready()
  logger.warning("ready")
  while not bot.is_closed:
      f.flush()
      line = f.readline()
      while line:
        await bot.send_message(bot.get_channel('321832332279676928'), line)
        line = f.readline()
      await asyncio.sleep(1)

bot.load_extension("wordart") # bot can start and load wordart later.
bot.embed_this_for_me = embed_this_for_me # attach to bot object so cogs don't need to import main
bot.fit_msg = fit_msg # attach fit_msg to bot object
bot.Henry = Henry
bot.loop.create_task(update())
bot.run(token)
#ali was here
