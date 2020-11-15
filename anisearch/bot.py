import platform

import discord
import psycopg2
from discord.ext import commands
from discord.ext.commands import Bot as BotBase, when_mentioned_or

from anisearch import config
from anisearch.utils.logger import logger

initial_extensions = [
    'anisearch.cogs.events',
    'anisearch.cogs.help',
    'anisearch.cogs.admin',
    'anisearch.cogs.anime',
    'anisearch.cogs.manga',
    'anisearch.cogs.character',
    'anisearch.cogs.staff',
    'anisearch.cogs.studio'
]

version = '1.6'


def _get_command_prefix(self, message):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    try:
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return when_mentioned_or(prefix, 'as!')(self, message)
    except TypeError:
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        logger.info('Set Prefix for Guild {} to {}'.format(message.guild.id, prefix))
        return when_mentioned_or(prefix, 'as!')(self, message)


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
        intents = discord.Intents(messages=True, guilds=True, reactions=True)
        super().__init__(command_prefix=_get_command_prefix, intents=intents, owner_id=config.OWNERID)

    async def load_extensions(self):
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                logger.info('Cog {} is already loaded.'.format(extension))
            except Exception as exception:
                logger.exception(exception)
        logger.info('Cogs loaded {}/{}'.format(len(self.cogs), len(initial_extensions)))

    async def on_ready(self):
        logger.info('Logged in as {}'.format(self.user))
        logger.info('Bot-Name: {}'.format(self.user.name))
        logger.info('Bot-Discriminator: {}'.format(self.user.discriminator))
        logger.info('Bot-ID: {}'.format(self.user.id))
        logger.info('Bot-Version: {}'.format(version))
        logger.info('Discord.py-Version: {}'.format(discord.__version__))
        logger.info('Python-Version: {}'.format(platform.python_version()))
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='as!help'),
                                   status=discord.Status.online)
        await self.load_extensions()

    async def on_connect(self):
        logger.info('Connected to Discord')

    async def on_disconnect(self):
        logger.info('Disconnected from Discord')

    async def on_command(self, ctx):
        logger.info('Server: {} | Author: {} | Content: {}'.format(ctx.guild.name, ctx.author, ctx.message.content))
