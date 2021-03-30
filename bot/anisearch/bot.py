"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import time
from io import StringIO
from asyncio import sleep

import dbl
import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks, menus
from discord.ext.commands import AutoShardedBot, Context, when_mentioned_or

from anisearch.config import BOT_TOKEN, BOT_OWNER_ID, BOT_TOPGG_TOKEN, BOT_SAUCENAO_API_KEY, BOT_API_HOST, \
    BOT_API_PORT, BOT_API_SECRET_KEY
from anisearch.utils.anilist import AniListClient
from anisearch.utils.animenewsnetwork import AnimeNewsNetworkClient
from anisearch.utils.animethemes import AnimeThemesClient
from anisearch.utils.api import Server
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_PREFIX
from anisearch.utils.crunchyroll import CrunchyrollClient
from anisearch.utils.database import DataBase
from anisearch.utils.jikan import JikanClient
from anisearch.utils.kitsu import KitsuClient
from anisearch.utils.saucenao import SauceNAOClient
from anisearch.utils.tracemoe import TraceMoeClient

log = logging.getLogger(__name__)

initial_extensions = [
    'anisearch.cogs.search',
    'anisearch.cogs.profile',
    'anisearch.cogs.image',
    'anisearch.cogs.schedule',
    'anisearch.cogs.news',
    'anisearch.cogs.help',
    'anisearch.cogs.settings',
    'anisearch.cogs.admin'
]


class AniSearchBot(AutoShardedBot):
    """
    A subclass of `discord.ext.commands.AutoShardedBot`.
    """

    def __init__(self, log_stream: StringIO) -> None:
        """
        Initializes the AniSearchBot.
        """
        intents = discord.Intents(
            messages=True,
            guilds=True,
            reactions=True
        )
        super().__init__(command_prefix=self.get_prefix, intents=intents, owner_id=int(BOT_OWNER_ID))

        self.log_stream = log_stream

        self.start_time = time.time()
        self.session = ClientSession(loop=self.loop)

        self.db = DataBase()
        self.api = Server(bot=self, host=BOT_API_HOST, port=int(BOT_API_PORT), secret_key=BOT_API_SECRET_KEY)

        self.anilist = AniListClient(session=ClientSession(loop=self.loop))

        self.animethemes = AnimeThemesClient(session=ClientSession(loop=self.loop),
                                             headers={'User-Agent': 'AniSearch Discord Bot'})

        self.tracemoe = TraceMoeClient(session=ClientSession(loop=self.loop))

        self.saucenao = SauceNAOClient(api_key=BOT_SAUCENAO_API_KEY, db=999, output_type=2, numres=10,
                                       session=ClientSession(loop=self.loop))

        self.myanimelist = JikanClient(session=ClientSession(loop=self.loop))

        self.kitsu = KitsuClient(session=ClientSession(loop=self.loop))

        self.animenewsnetwork = AnimeNewsNetworkClient(session=ClientSession(loop=self.loop))

        self.crunchyroll = CrunchyrollClient(session=ClientSession(loop=self.loop))

        # Posts the guild count to top.gg every 30 minutes.
        self.topgg_token = BOT_TOPGG_TOKEN
        self.dblpy = dbl.DBLClient(self, self.topgg_token, autopost=True)

        self.load_cogs()
        self.set_status.start()

    def load_cogs(self) -> None:
        """
        Loads all cogs.
        """
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(f'{len(self.cogs)}/{len(initial_extensions)} cogs loaded.')

    def unload_cogs(self) -> None:
        """
        Unloads all cogs.
        """
        for extension in initial_extensions:
            try:
                self.unload_extension(extension)
            except discord.ext.commands.errors.ExtensionNotLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(f'{len(initial_extensions) - len(self.cogs)}/{len(initial_extensions)} cogs unloaded.')

    async def on_ready(self) -> None:
        log.info(f'Logged in as {self.user}')
        log.info(f'Bot-Name: {self.user.name}')
        log.info(f'Bot-Discriminator: {self.user.discriminator}')
        log.info(f'Bot-ID: {self.user.id}')
        log.info(f'Shards: {self.shard_count}')
        log.info('Bot is ready.')

    async def get_prefix(self, message: discord.Message) -> when_mentioned_or():
        """
        Gets the command prefix of the bot for the current guild.

        Args:
            message (discord.Message): A Discord message.

        Returns:
            when_mentioned_or()
        """
        if isinstance(message.channel, discord.channel.DMChannel):
            return when_mentioned_or(DEFAULT_PREFIX)(self, message)
        prefix = self.db.get_prefix(message)
        return when_mentioned_or(prefix, DEFAULT_PREFIX)(self, message)

    @tasks.loop(seconds=30)
    async def set_status(self) -> None:
        """
        Sets the discord status of the bot.
        """
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                   name=f'{DEFAULT_PREFIX}help'), status=discord.Status.online)
        await sleep(20)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Anime'),
                                   status=discord.Status.online)

    @set_status.before_loop
    async def set_status_before(self) -> None:
        """
        Waits for the bot to be ready before starting the `set_status` task.
        """
        await self.wait_until_ready()

    async def on_connect(self) -> None:
        log.info('Connected to Discord.')

    async def on_disconnect(self) -> None:
        log.info('Disconnected from Discord.')

    async def on_api_ready(self):
        log.info('Api is ready.')

    async def on_command(self, ctx: Context) -> None:
        if isinstance(ctx.channel, discord.channel.DMChannel):
            log.info(f'[{ctx.author.id}] {ctx.author} » {ctx.message.content}')
        else:
            log.info(f'[{ctx.author.id}] {ctx.author} - [{ctx.guild.id}] {ctx.guild.name} » {ctx.message.content}')

    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info(f'Joined guild {guild.name} [{guild.id}].')
        self.db.insert_prefix(guild)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        log.info(f'Left guild {guild.name} [{guild.id}].')
        self.db.delete_prefix(guild)

    def get_guild_count(self) -> int:
        """
        Returns the bot guild count.
        """
        guilds = len(self.guilds)
        return guilds

    def get_user_count(self) -> int:
        """
        Returns the bot user count.
        """
        users = 0
        for guild in self.guilds:
            try:
                users += guild.member_count
            except Exception as e:
                logging.warning(e)
        return users

    def get_channel_count(self) -> int:
        """
        Returns the bot channel count.
        """
        channels = 0
        for guild in self.guilds:
            channels += len(guild.channels)
        return channels

    def get_uptime(self) -> float:
        """
        Returns the bot uptime.
        """
        uptime = time.time() - self.start_time
        return uptime

    def run(self):
        """
        Runs the bot.
        """
        super().run(BOT_TOKEN)

    async def close(self):
        """
        Closes the discord connection, the database pool connections and the aiohttp sessions.
        """
        self.unload_cogs()
        self.db.close()
        await self.anilist.close()
        await self.animethemes.close()
        await self.tracemoe.close()
        await self.saucenao.close()
        await self.myanimelist.close()
        await self.kitsu.close()
        await self.animenewsnetwork.close()
        await self.crunchyroll.close()
        if self.session is not None:
            await self.session.close()
        await super().close()

    async def on_guild_post(self):
        log.info(f'TopGG server count posted ({self.dblpy.guild_count()}).')

    async def on_command_error(self, ctx: Context, error: Exception) -> None:

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        title = 'An unknown error occurred.'

        if isinstance(error, discord.errors.Forbidden):
            log.warning(error)
            return await ctx.message.add_reaction(emoji='🔇')

        elif isinstance(error, commands.CommandNotFound):
            title = 'Command not found.'

        elif isinstance(error, commands.CommandOnCooldown):
            title = f'Command on cooldown for `{error.retry_after:.2f}s`.'

        elif isinstance(error, commands.TooManyArguments):
            title = f'Too many arguments. Use `{self.db.get_prefix(ctx.message)}help {ctx.command}` for help.'
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'Missing required argument. Use `{self.db.get_prefix(ctx.message)}help {ctx.command}` for help.'
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BadArgument):
            title = f'Wrong arguments. Use `{self.db.get_prefix(ctx.message)}help {ctx.command}` for help.'
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

        elif isinstance(error, commands.NotOwner):
            title = 'You are not the owner of the bot.'
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, menus.CannotAddReactions):
            title = 'Cannot add reactions.'
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, menus.CannotEmbedLinks):
            title = 'Cannot embed links.'
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, menus.CannotReadMessageHistory):
            title = 'Cannot read message history.'
            ctx.command.reset_cooldown(ctx)

        else:
            log.exception('An unknown exception occurred while executing a command.', exc_info=error)

        embed = discord.Embed(title=title, color=ERROR_EMBED_COLOR)
        return await ctx.channel.send(embed=embed)
