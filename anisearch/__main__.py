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

import aiohttp
import discord

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.config import TOKEN


def main() -> None:
    """
    Main function.
    """
    setup_logging()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_update())
    logging.info('Starting AniSearch Discord Bot.')
    logging.info(f'Discord.py version: {discord.__version__}')
    logging.info(f'Python version: {platform.python_version()}')
    start()


def setup_logging() -> None:
    """
    Sets up the logging.
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(asctime)s:%(name)s:%(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')


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


def start() -> None:
    """
    Starts the bot.
    """
    try:
        bot = AniSearchBot()
        bot.run(TOKEN)
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
