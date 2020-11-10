import logging
import platform
from datetime import datetime
import discord
import psycopg2
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import when_mentioned_or
from anisearch import config

__version__ = '1.5.2'
__author__ = 'IchBinLeoon'
__invite__ = 'https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=83968&scope=bot'
__vote__ = 'https://top.gg/bot/737236600878137363/vote'
__github__ = 'https://github.com/IchBinLeoon/anisearch-discord-bot'

logger = logging.getLogger('anisearch')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

file_handler = logging.FileHandler('../anisearch.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

initial_extensions = [
    'anisearch.cogs.admin',
    'anisearch.cogs.anime',
    'anisearch.cogs.manga',
    'anisearch.cogs.character',
    'anisearch.cogs.staff',
    'anisearch.cogs.random',
    'anisearch.cogs.anilist',
    'anisearch.cogs.studio',
    'anisearch.cogs.myanimelist',
    'anisearch.cogs.setprofile',
    'anisearch.cogs.remove',
    'anisearch.cogs.prefix',
    'anisearch.cogs.ping',
    'anisearch.cogs.help',
    'anisearch.cogs.about',
    'anisearch.cogs.contact',
    'anisearch.cogs.source',
    'anisearch.handlers.error_handler',
    'anisearch.handlers.topgg',
    'anisearch.events.guild_join',
    'anisearch.events.guild_leave'
]


def get_current_time():
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')


def get_command_prefix(client, message):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    try:
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return when_mentioned_or(prefix, 'as!')(client, message)
    except TypeError:
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return when_mentioned_or(prefix, 'as!')(client, message)


def get_prefix(ctx):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
    prefix = cur.fetchone()[0]
    db.commit()
    cur.close()
    db.close()
    return prefix


class AniSearchBot(BotBase):

    def __init__(self):
        intents = discord.Intents(messages=True, guilds=True)
        super().__init__(command_prefix=get_command_prefix, intents=intents, owner_id=config.OWNERID)

    async def load_extensions(self):
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                logger.info('Extension {} is already loaded.'.format(extension))
            except Exception as exception:
                logger.info(exception)
        logger.info('Extensions loaded %s/%s' % (len(self.cogs), len(initial_extensions)))

    async def on_ready(self):
        logger.info('Logged in as %s' % self.user)
        logger.info('Client-Name: %s' % self.user.name)
        logger.info('Client-Discriminator: %s' % self.user.discriminator)
        logger.info('Client-ID: %s' % self.user.id)
        logger.info('Client-Version: %s' % __version__)
        logger.info('Discord-Version: %s' % discord.__version__)
        logger.info('Python-Version: %s' % platform.python_version())
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='as!help'),
                                   status=discord.Status.online)
        await self.load_extensions()
        online_embed = discord.Embed(title='Client is online - Extensions loaded %s/%s' % (len(self.cogs),
                                                                                           len(initial_extensions)),
                                     color=0x4169E1)
        user = await self.fetch_user(config.OWNERID)
        await user.send(embed=online_embed)

    async def on_connect(self):
        logger.info('Connected to Discord')

    async def on_disconnect(self):
        logger.info('Disconnected from Discord')

    async def on_command(self, ctx):
        if ctx.message.author == self.user:
            return
        elif isinstance(ctx.message.channel, discord.channel.DMChannel):
            return
        elif ctx.message.content.startswith('as!'):
            args = ctx.message.content[3:].split(' ')[1:]
            logger.info('Server: %s | Author: %s | Command: %s | Args: %s' % (ctx.guild.name, ctx.author, ctx.command,
                                                                              args))
        elif ctx.message.content.startswith(get_prefix(ctx.message)):
            args = ctx.message.content[len(get_prefix(ctx.message)):].split(' ')[1:]
            logger.info('Server: %s | Author: %s | Command: %s | Args: %s' % (ctx.guild.name, ctx.author, ctx.command,
                                                                              args))
