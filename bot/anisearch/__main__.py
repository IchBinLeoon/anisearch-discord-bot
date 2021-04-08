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

import asyncio
import logging
import platform
import re
import sys
from io import StringIO

import aiohttp
import discord

import anisearch
from anisearch.bot import AniSearchBot


def main() -> None:
    """
    Main function.
    """
    log_stream = setup_logging()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_update())
    logging.info(f'Starting AniSearch Bot v{anisearch.__version__}')
    logging.info(f'Discord.py version: {discord.__version__}')
    logging.info(f'Python version: {platform.python_version()}')
    start(log_stream)


def setup_logging() -> StringIO:
    """
    Sets up the logging.
    """
    log_stream = StringIO()
    console_handler = logging.StreamHandler(sys.stdout)
    log_handler = logging.StreamHandler(log_stream)
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s » %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', handlers=[console_handler, log_handler])
    return log_stream


async def check_update() -> None:
    """
    Checks GitHub for a newer version of the bot.
    """
    async with aiohttp.ClientSession() as s:
        async with s.get('https://raw.githubusercontent.com/IchBinLeoon/anisearch-discord-bot/main/anisearch/__init__'
                         '.py') as r:
            if r.status == 200:
                github_version = str(re.findall("__version__ = '(.*)'", await r.text())[0])
                if github_version != anisearch.__version__:
                    logging.info(
                        f'Update available! You are running version {anisearch.__version__}. Version {github_version} '
                        f'is available at https://github.com/IchBinLeoon/anisearch-discord-bot.')


def start(log_stream: StringIO) -> None:
    """
    Starts the bot.
    """
    try:
        bot = AniSearchBot(log_stream)
        bot.api.start()
        bot.run()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
