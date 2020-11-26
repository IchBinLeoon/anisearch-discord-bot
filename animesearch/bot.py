import platform
import discord
from animesearch.utils.database.prefix import get_command_prefix
from animesearch.utils.database.prefix import insert_prefix
from animesearch.utils.database.prefix import delete_prefix
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from animesearch import config
from animesearch.utils.logger import logger

version = '1.6'

initial_extensions = [
    'animesearch.cogs.help',
    'animesearch.cogs.admin',
    'animesearch.cogs.events',
    'animesearch.cogs.settings',
    'animesearch.cogs.anime',
    'animesearch.cogs.manga',
    'animesearch.cogs.character',
    'animesearch.cogs.staff',
    'animesearch.cogs.studio',
    'animesearch.cogs.random',
    'animesearch.cogs.anilist',
    'animesearch.cogs.myanimelist',
    'animesearch.cogs.kitsu',
    'animesearch.cogs.profile',
    'animesearch.cogs.image',
    'animesearch.cogs.theme'
]


class AnimeSearchBot(BotBase):

    def __init__(self):
        intents = discord.Intents(messages=True, guilds=True, reactions=True)
        super().__init__(command_prefix=get_command_prefix, intents=intents, owner_id=int(config.OWNER_ID))

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
        logger.info('Bot is online')

    @commands.Cog.listener()
    async def on_connect(self):
        logger.info('Connected to Discord')

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger.info('Disconnected from Discord')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            logger.info('Private Message | Author: {} | Content: {}'.format(ctx.author, ctx.message.content))
        else:
            logger.info('Server: {} | Author: {} | Content: {}'.format(ctx.guild.name, ctx.author, ctx.message.content))
            perms = 0
            if ctx.me.guild_permissions.manage_messages:
                perms += 1
            if ctx.me.guild_permissions.add_reactions:
                perms += 1
            if perms < 2:
                embed = discord.Embed(title='Warning',
                                      description=f'**Hi there! Since the new update I need the `Add Reactions` '
                                                  f'and `Manage Messages` permissions to function properly.**',
                                      color=0xff0000)
                await ctx.channel.send(embed=embed)
                logger.info('Missing Permissions Warning')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logger.info('Joined server {}'.format(guild.name))
        insert_prefix(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger.info('Left server {}'.format(guild.name))
        delete_prefix(guild)

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
        elif isinstance(error, commands.NoPrivateMessage):
            title = 'Command cannot be used in private messages.'
            ctx.command.reset_cooldown(ctx)
        else:
            logger.exception(error)
        embed = discord.Embed(title=title, color=0xff0000)
        await ctx.channel.send(embed=embed)
