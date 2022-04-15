import logging
import time
from io import StringIO
from asyncio import sleep

import nextcord
from aiohttp import ClientSession
from nextcord.ext import commands, tasks, menus
from nextcord.ext.commands import AutoShardedBot, Context, when_mentioned_or
from nextcord.utils import get
from jikanpy import AioJikan
from pysaucenao import SauceNao
from tracemoe import TraceMoe
from waifu import WaifuAioClient

from anisearch.config import BOT_TOKEN, BOT_OWNER_ID, BOT_TOPGG_TOKEN, BOT_SAUCENAO_API_KEY, BOT_API_HOST, \
    BOT_API_PORT, BOT_API_SECRET_KEY
from anisearch.utils.anilist import AniListClient
from anisearch.utils.api import Server
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_PREFIX, BOT_ID, SUPPORT_SERVER_INVITE
from anisearch.utils.database import DataBase

log = logging.getLogger(__name__)

initial_extensions = [
    'anisearch.cogs.search',
    'anisearch.cogs.profile',
    'anisearch.cogs.notification',
    'anisearch.cogs.image',
    'anisearch.cogs.themes',
    'anisearch.cogs.news',
    'anisearch.cogs.help',
    'anisearch.cogs.settings'
]


class AniSearchBot(AutoShardedBot):

    def __init__(self, log_stream: StringIO) -> None:
        intents = nextcord.Intents(
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

        self.tracemoe = TraceMoe(session=ClientSession(loop=self.loop))

        self.saucenao = SauceNao(api_key=BOT_SAUCENAO_API_KEY, db=999, loop=self.loop,
                                 results_limit=10, min_similarity=0)

        self.jikan = AioJikan(session=ClientSession(loop=self.loop))

        self.waifu = WaifuAioClient(session=ClientSession(loop=self.loop))

        self.load_cogs()
        self.set_status.start()

        if BOT_TOPGG_TOKEN:
            self.post_topgg_stats.start()

    def load_cogs(self) -> None:
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except nextcord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(f'{len(self.cogs)}/{len(initial_extensions)} cogs loaded')

    def unload_cogs(self) -> None:
        for extension in initial_extensions:
            try:
                self.unload_extension(extension)
            except nextcord.ext.commands.errors.ExtensionNotLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(
            f'{len(initial_extensions) - len(self.cogs)}/{len(initial_extensions)} cogs unloaded')

    async def get_prefix(self, message: nextcord.Message) -> list[str]:
        if isinstance(message.channel, nextcord.channel.DMChannel):
            return when_mentioned_or(DEFAULT_PREFIX)(self, message)
        prefix = self.db.get_prefix(message)
        return when_mentioned_or(prefix, DEFAULT_PREFIX)(self, message)

    @tasks.loop(seconds=80)
    async def set_status(self) -> None:
        await self.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening,
                                                              name=f'{DEFAULT_PREFIX}help'),
                                   status=nextcord.Status.online)
        await sleep(20)
        await self.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing,
                                                              name=f'on {self.get_guild_count()} servers'),
                                   status=nextcord.Status.online)
        await sleep(20)
        await self.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing,
                                                              name=f'with {self.get_user_count()} users'),
                                   status=nextcord.Status.online)
        await sleep(20)
        await self.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name='Anime'),
                                   status=nextcord.Status.online)

    @set_status.before_loop
    async def set_status_before(self) -> None:
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
        if isinstance(ctx.channel, nextcord.channel.DMChannel):
            log.info(f'User {ctx.author.id} executed command: {ctx.message.content}')
        else:
            log.info(
                f'(Guild {ctx.guild.id}) User {ctx.author.id} executed command: {ctx.message.content}')

    async def on_guild_join(self, guild: nextcord.Guild) -> None:
        log.info(f'Bot joined guild {guild.id}')
        self.db.insert_guild(guild)
        try:
            user = await self.fetch_user(guild.owner_id)
            await user.send(f'**Hey there! Thanks for using <@!{BOT_ID}>!**\n\n'
                            f'A few things to get started with the bot:\n\n'
                            f'• To display all commands use: `as!{get(self.commands, name="commands").usage}`\n\n'
                            f'• To display information about a command use: '
                            f'`as!{get(self.commands, name="help").usage}`\n\n'
                            f'• To change the server prefix use: `as!{get(self.commands, name="setprefix").usage}`\n\n'
                            f'• Do **not** include `<>`, `[]` or `|` when executing a command.\n\n'
                            f'• In case of any problems, bugs, suggestions or if you just want to chat, '
                            f'feel free to join the support server! {SUPPORT_SERVER_INVITE}\n\n'
                            "Have fun with the bot!")
        except nextcord.errors.Forbidden:
            pass
        except Exception as e:
            log.exception(e)

    async def on_guild_remove(self, guild: nextcord.Guild) -> None:
        log.info(f'Bot left guild {guild.id}')
        self.db.delete_guild(guild)

    def get_guild_count(self) -> int:
        guilds = len(self.guilds)
        return guilds

    def get_user_count(self) -> int:
        users = 0
        for guild in self.guilds:
            try:
                users += guild.member_count
            except Exception as e:
                logging.warning(e)
        return users

    def get_channel_count(self) -> int:
        channels = 0
        for guild in self.guilds:
            channels += len(guild.channels)
        return channels

    def get_uptime(self) -> float:
        uptime = time.time() - self.start_time
        return uptime

    @tasks.loop(minutes=30)
    async def post_topgg_stats(self) -> None:
        guilds = len(self.guilds)
        shards = self.shard_count
        r = await self.session.post(f'https://top.gg/api/bots/{self.user.id}/stats',
                                    json={'server_count': guilds, 'shard_count': shards},
                                    headers={'Authorization': BOT_TOPGG_TOKEN})
        if r.status == 200:
            log.info(f'TopGG statistics posted (Guilds: {guilds}, Shards: {shards})')
        else:
            log.warning(f'Error while posting TopGG statistics: {r.status} {r.reason} {await r.text()}')

    @post_topgg_stats.before_loop
    async def post_topgg_stats_before(self) -> None:
        await self.wait_until_ready()

    def run(self):
        super().run(BOT_TOKEN)

    async def close(self):
        self.unload_cogs()
        self.db.close()
        await self.anilist.close()
        await self.tracemoe.close()
        await self.jikan.close()
        await self.waifu.close()
        await self.session.close()
        await super().close()

    async def on_command_error(self, ctx: Context, error: Exception) -> nextcord.Message | None:

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, nextcord.errors.Forbidden):
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

        elif isinstance(error, nextcord.errors.Forbidden):
            log.warning(error)
            ctx.command.reset_cooldown(ctx)

        else:
            log.exception(
                'An unknown exception occurred while executing a command:', exc_info=error)

        embed = nextcord.Embed(title=title, color=ERROR_EMBED_COLOR)
        return await ctx.channel.send(embed=embed)
