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

import topgg
import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks, menus
from discord.ext.commands import AutoShardedBot, Context, when_mentioned_or
from discord.utils import get

from anisearch.config import BOT_TOKEN, BOT_OWNER_ID, BOT_TOPGG_TOKEN, BOT_SAUCENAO_API_KEY, BOT_API_HOST, \
    BOT_API_PORT, BOT_API_SECRET_KEY
from anisearch.utils.anilist import AniListClient
from anisearch.utils.animenewsnetwork import AnimeNewsNetworkClient
from anisearch.utils.animethemes import AnimeThemesClient
from anisearch.utils.api import Server
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_PREFIX, BOT_ID, SUPPORT_SERVER_INVITE
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
    'anisearch.cogs.themes',
    'anisearch.cogs.image',
    'anisearch.cogs.schedule',
    'anisearch.cogs.news',
    'anisearch.cogs.help',
    'anisearch.cogs.settings',
    'anisearch.cogs.admin'
]


class AniSearchBot(AutoShardedBot):

    def __init__(self, log_stream: StringIO) -> None:
        intents = discord.Intents(
            messages=True,
            guilds=True,
            reactions=True
        )
        super().__init__(command_prefix=self.get_prefix,
                         intents=intents, owner_id=int(BOT_OWNER_ID))

        self.log_stream = log_stream

        self.start_time = time.time()
        self.session = ClientSession(loop=self.loop)

        self.db = DataBase()
        self.api = Server(bot=self, host=BOT_API_HOST, port=int(
            BOT_API_PORT), secret_key=BOT_API_SECRET_KEY)

        self.anilist = AniListClient(session=ClientSession(loop=self.loop))

        self.animethemes = AnimeThemesClient(session=ClientSession(loop=self.loop),
                                             headers={'User-Agent': 'AniSearch Discord Bot'})

        self.tracemoe = TraceMoeClient(session=ClientSession(loop=self.loop))

        self.saucenao = SauceNAOClient(api_key=BOT_SAUCENAO_API_KEY, db=999, output_type=2, numres=10,
                                       session=ClientSession(loop=self.loop))

        self.myanimelist = JikanClient(session=ClientSession(loop=self.loop))

        self.kitsu = KitsuClient(session=ClientSession(loop=self.loop))

        self.animenewsnetwork = AnimeNewsNetworkClient(
            session=ClientSession(loop=self.loop))

        self.crunchyroll = CrunchyrollClient(
            session=ClientSession(loop=self.loop))

        # Posts guild and shard count to Top.gg every 30 minutes.
        self.topgg = topgg.DBLClient(
            self, BOT_TOPGG_TOKEN, autopost=True, post_shard_count=True)

        self.load_cogs()
        self.set_status.start()

    def load_cogs(self) -> None:
        """Loads all cogs."""
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(f'{len(self.cogs)}/{len(initial_extensions)} cogs loaded')

    def unload_cogs(self) -> None:
        """Unloads all cogs."""
        for extension in initial_extensions:
            try:
                self.unload_extension(extension)
            except discord.ext.commands.errors.ExtensionNotLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(
            f'{len(initial_extensions) - len(self.cogs)}/{len(initial_extensions)} cogs unloaded')

    async def get_prefix(self, message: discord.Message) -> when_mentioned_or():
        """Gets the command prefix of the bot for the current guild."""
        if isinstance(message.channel, discord.channel.DMChannel):
            return when_mentioned_or(DEFAULT_PREFIX)(self, message)
        prefix = self.db.get_prefix(message)
        return when_mentioned_or(prefix, DEFAULT_PREFIX)(self, message)

    @tasks.loop(seconds=80)
    async def set_status(self) -> None:
        """Sets the discord status of the bot every 80 seconds."""
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                   name=f'{DEFAULT_PREFIX}help'), status=discord.Status.online)
        await sleep(20)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                             name=f'on {self.get_guild_count()} servers'),
                                   status=discord.Status.online)
        await sleep(20)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                             name=f'with {self.get_user_count()} users'),
                                   status=discord.Status.online)
        await sleep(20)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Anime'),
                                   status=discord.Status.online)

    @set_status.before_loop
    async def set_status_before(self) -> None:
        """Waits for the bot to be ready before starting the `set_status` task."""
        await self.wait_until_ready()

    async def on_shard_ready(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} is ready')

    async def on_shard_connect(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} connected to Discord')

    async def on_shard_disconnect(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} disconnected from Discord')

    async def on_shard_resumed(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} resumed to Discord')

    async def on_api_ready(self, host: str, port: int):
        log.info(f'Api is ready: Listening and serving HTTP on {host}:{port}')

    async def on_command(self, ctx: Context) -> None:
        if isinstance(ctx.channel, discord.channel.DMChannel):
            log.info(f'User {ctx.author.id} executed command: {ctx.message.content}')
        else:
            log.info(
                f'(Guild {ctx.guild.id}) User {ctx.author.id} executed command: {ctx.message.content}')

    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info(f'Bot joined guild {guild.id}')
        self.db.insert_prefix(guild)
        try:
            user = await self.fetch_user(guild.owner_id)
            await user.send(f'**Hey there! Thanks for using <@!{BOT_ID}>!**\n\n'
                            f'A few things to get started with the bot:\n\n'
                            f'• To display all commands use: `as!{get(self.commands, name="commands").usage}`\n\n'
                            f'• To display information about a command use: '
                            f'`as!{get(self.commands, name="help").usage}`\n\n'
                            f'• To change the server prefix use: `as!set prefix <prefix>`\n\n'
                            f'• To set the channel for the anime episode notifications use: '
                            f'`as!set channel <#channel>`\n\n'
                            f'• To set the role for notification mentions use: `as!set role <@role>`\n\n'
                            f'• Do **not** include `<>`, `[]` or `|` when executing a command.\n\n'
                            f'• In case of any problems, bugs, suggestions or if you just want to chat, '
                            f'feel free to join the support server! {SUPPORT_SERVER_INVITE}\n\n'
                            "Have fun with the bot!")
        except Exception as e:
            log.exception(e)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        log.info(f'Bot left guild {guild.id}')
        self.db.delete_prefix(guild)

    async def on_autopost_success(self):
        log.info(
            f'TopGG statistics posted (Guilds: {self.topgg.guild_count}, Shards: {self.shard_count})')

    async def on_autopost_error(self, error: Exception):
        if isinstance(error, topgg.errors.UnauthorizedDetected):
            log.warning(error)
        else:
            log.exception(error)

    def get_guild_count(self) -> int:
        """Returns the bot guild count."""
        guilds = len(self.guilds)
        return guilds

    def get_user_count(self) -> int:
        """Returns the bot user count."""
        users = 0
        for guild in self.guilds:
            try:
                users += guild.member_count
            except Exception as e:
                logging.warning(e)
        return users

    def get_channel_count(self) -> int:
        """Returns the bot channel count."""
        channels = 0
        for guild in self.guilds:
            channels += len(guild.channels)
        return channels

    def get_uptime(self) -> float:
        """Returns the bot uptime."""
        uptime = time.time() - self.start_time
        return uptime

    def run(self):
        """Runs the bot."""
        super().run(BOT_TOKEN)

    async def close(self):
        """Closes the discord connection, the database pool connections and the aiohttp sessions."""
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
        await self.session.close()
        await super().close()

    async def on_command_error(self, ctx: Context, error: Exception) -> None:

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, discord.errors.Forbidden):
            return await ctx.message.add_reaction(emoji='🔇')

        title = 'An unknown error occurred.'

        if isinstance(error, commands.CommandOnCooldown):
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

        elif isinstance(error, discord.errors.Forbidden):
            log.warning(error)
            ctx.command.reset_cooldown(ctx)

        else:
            log.exception(
                'An unknown exception occurred while executing a command:', exc_info=error)

        embed = discord.Embed(title=title, color=ERROR_EMBED_COLOR)
        return await ctx.channel.send(embed=embed)
