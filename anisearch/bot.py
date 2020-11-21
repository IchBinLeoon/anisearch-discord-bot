import platform
import discord
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from anisearch import config
from anisearch.utils.logger import logger

version = '1.6'

initial_extensions = [
    'anisearch.cogs.help',
    'anisearch.cogs.admin',
    'anisearch.cogs.anime',
    'anisearch.cogs.manga',
    'anisearch.cogs.character',
    'anisearch.cogs.staff',
    'anisearch.cogs.studio',
    'anisearch.cogs.random',
    'anisearch.cogs.anilist',
    'anisearch.cogs.myanimelist',
    'anisearch.cogs.kitsu',
    'anisearch.cogs.trace',
    'anisearch.cogs.TopGG'
]


class AniSearchBot(BotBase):

    def __init__(self):
        intents = discord.Intents(messages=True, guilds=True, reactions=True)
        super().__init__(command_prefix='as!', intents=intents, owner_id=config.OWNERID)

    def load_cogs(self):
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as exception:
                logger.exception(exception)
        logger.info('Cogs loaded {}/{}'.format(len(self.cogs), len(initial_extensions)))

    @commands.Cog.listener()
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
        self.load_cogs()

    @commands.Cog.listener()
    async def on_connect(self):
        logger.info('Connected to Discord')

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger.info('Disconnected from Discord')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info('Server: {} | Author: {} | Content: {}'.format(ctx.guild.name, ctx.author, ctx.message.content))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logger.info('Joined server {}'.format(guild.name))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger.info('Left server {}'.format(guild.name))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        title = 'An error occurred.'
        if isinstance(error, commands.CommandNotFound):
            title = 'Command not found.'
        elif isinstance(error, commands.CommandOnCooldown):
            title = 'Command on cooldown for `{:.2f}s`.'.format(error.retry_after)
        elif isinstance(error, commands.TooManyArguments):
            title = 'Too many arguments.'
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.MissingRequiredArgument):
            title = 'Missing required argument.'
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.BadArgument):
            title = 'Wrong arguments.'
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.MissingPermissions):
            title = 'Missing permissions.'
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.BotMissingPermissions):
            title = 'Bot missing permissions.'
            ctx.command.reset_cooldown(ctx)
        else:
            logger.exception(error)
        embed = discord.Embed(title=title, color=0xff0000)
        await ctx.channel.send(embed=embed)
