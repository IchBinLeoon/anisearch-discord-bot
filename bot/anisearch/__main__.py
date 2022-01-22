import asyncio
import logging
import platform
import re
import sys
from io import StringIO

import aiohttp
import nextcord

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.config import BOT_LEVEL


def main() -> None:
    logging_level = logging.getLevelName(BOT_LEVEL)
    log_stream = setup_logging(logging_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(check_update())
    logging.info(f'Starting AniSearch Bot v{anisearch.__version__}')
    logging.info(f'Nextcord version: {nextcord.__version__}')
    logging.info(f'Python version: {platform.python_version()}')
    start(log_stream)


def setup_logging(logging_level: int) -> StringIO:
    log_stream = StringIO()
    console_handler = logging.StreamHandler(sys.stdout)
    log_handler = logging.StreamHandler(log_stream)
    logging.basicConfig(level=logging_level, format='[%(asctime)s] %(levelname)s %(name)s » %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', handlers=[console_handler, log_handler])
    return log_stream


async def check_update() -> None:
    async with aiohttp.ClientSession() as s:
        async with s.get('https://raw.githubusercontent.com/IchBinLeoon/anisearch-discord-bot/main/bot/anisearch/'
                         '__init__.py') as r:
            if r.status == 200:
                github_version = str(re.findall("__version__ = '(.*)'", await r.text())[0])
                if github_version != anisearch.__version__:
                    logging.info(
                        f'Update available! You are running version {anisearch.__version__} - Version {github_version} '
                        f'is available at https://github.com/IchBinLeoon/anisearch-discord-bot')


def start(log_stream: StringIO) -> None:
    try:
        bot = AniSearchBot(log_stream)
        bot.api.start()
        bot.run()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
