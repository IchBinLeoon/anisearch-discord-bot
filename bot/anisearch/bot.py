import logging
from io import StringIO

import asyncpg
import discord
import time
from aiohttp import ClientSession
from discord.ext import commands

from anisearch.api import Server
from anisearch.database import Database

log = logging.getLogger(__name__)

initial_extensions = ['anisearch.cogs.help', 'anisearch.cogs.events']

intents = discord.Intents.default()


class AniSearchBot(commands.AutoShardedBot):
    def __init__(self, log_stream: StringIO, pool: asyncpg.Pool) -> None:
        super().__init__(command_prefix=[], intents=intents)

        self.log_stream = log_stream

        self.start_time = time.time()
        self.session = ClientSession()

        self.db = Database(pool)
        self.api = Server(self)

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

    async def start(self, token: str) -> None:
        await super().start(token=token, reconnect=True)
