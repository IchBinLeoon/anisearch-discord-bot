import asyncio
import logging
import os
import platform
import sys
from io import StringIO

import asyncpg
import discord

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.database import create_postgres_pool

TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('BOT_DATABASE_URL')

HOST = os.getenv('BOT_API_HOST')
PORT = os.getenv('BOT_API_PORT')

LOG_LEVEL = os.getenv('BOT_LOG_LEVEL')


async def main() -> None:
    log_stream = setup_logging()

    logging.info(f'Starting AniSearch Bot v{anisearch.__version__}')
    logging.info(f'Discord.py version: {discord.__version__}')
    logging.info(f'Python version: {platform.python_version()}')

    pool = await create_postgres_pool(DATABASE_URL)

    await start(log_stream, pool)


def setup_logging() -> StringIO:
    log_level = logging.getLevelName(LOG_LEVEL)
    log_stream = StringIO()

    console_handler = logging.StreamHandler(sys.stdout)
    log_handler = logging.StreamHandler(log_stream)

    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(levelname)s %(name)s » %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        handlers=[console_handler, log_handler],
    )

    if log_level != logging.DEBUG:
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('aiohttp.access').setLevel(logging.WARNING)

    return log_stream


async def start(log_stream: StringIO, pool: asyncpg.Pool) -> None:
    async with AniSearchBot(log_stream=log_stream, pool=pool) as bot:
        try:
            await bot.api.start(HOST, int(PORT))
            await bot.start(TOKEN)
        except Exception as e:
            logging.exception(e)
            exit(1)


if __name__ == '__main__':
    asyncio.run(main())
