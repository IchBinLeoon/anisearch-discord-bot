import logging
import os
import time
from io import StringIO

import asyncpg
import discord
from aiohttp import ClientSession
from discord.ext import commands
from pysaucenao import SauceNao
from tracemoe import TraceMoe
from waifu import WaifuAioClient

from anisearch.api import Server
from anisearch.database import Database
from anisearch.utils.anilist import AniListClient

log = logging.getLogger(__name__)

TRACEMOE_API_KEY = os.getenv('BOT_TRACEMOE_API_KEY')
SAUCENAO_API_KEY = os.getenv('BOT_SAUCENAO_API_KEY')

initial_extensions = [
    'anisearch.cogs.search',
    'anisearch.cogs.image',
    'anisearch.cogs.news',
    'anisearch.cogs.utility',
    'anisearch.cogs.help',
    'anisearch.cogs.events',
]

intents = discord.Intents.default()


class AniSearchBot(commands.AutoShardedBot):
    def __init__(self, log_stream: StringIO, pool: asyncpg.Pool) -> None:
        super().__init__(command_prefix=[], intents=intents)

        self.log_stream = log_stream

        self.start_time = time.time()
        self.session = ClientSession()

        self.db = Database(pool)
        self.api = Server(self)

        self.anilist = AniListClient()
        self.tracemoe = TraceMoe(api_key=TRACEMOE_API_KEY)
        self.saucenao = SauceNao(api_key=SAUCENAO_API_KEY, results_limit=10)
        self.waifu = WaifuAioClient()

    async def setup_hook(self) -> None:
        for extension in initial_extensions:
            await self.load_extension(extension)

        await self.tree.sync()

    async def on_shard_ready(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} is ready')

    async def on_shard_connect(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} connected to Discord')

    async def on_shard_disconnect(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} disconnected from Discord')

    async def on_shard_resumed(self, shard_id: int) -> None:
        log.info(f'Shard ID {shard_id} resumed to Discord')

    async def on_api_ready(self, host: str, port: int) -> None:
        log.info(f'Listening and serving HTTP on {host}:{port}')

    async def close(self) -> None:
        await super().close()
        await self.session.close()
        await self.db.close()
        await self.api.stop()
        await self.anilist.close()
        await self.tracemoe.close()
        await self.waifu.close()

    async def start(self, token: str) -> None:
        await super().start(token=token, reconnect=True)
