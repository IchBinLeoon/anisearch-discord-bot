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
import platform
import re
import sys

import aiohttp
import discord
import psycopg2

import anisearch
from anisearch import config
from anisearch.bot import AniSearchBot
from anisearch.utils.logger import logger


def main():
    logger.info('Starting AniSearch Discord Bot')
    logger.info('Name: {}'.format(anisearch.__name__))
    logger.info('Author: {}'.format(anisearch.__author__))
    logger.info('Description: {}'.format(anisearch.__description__))
    logger.info('Url: {}'.format(anisearch.__url__))
    logger.info('License: {}'.format(anisearch.__license__))
    logger.info('Version: {}'.format(anisearch.__version__))
    logger.info('Discord.py-Version: {}'.format(discord.__version__))
    logger.info('Python-Version: {}'.format(platform.python_version()))
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(version_check())
        database_check()
        start_bot()
    except Exception as exception:
        logger.exception(exception)
        sys.exit()


async def version_check():
    logger.info('Checking for a newer version')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://raw.githubusercontent.com/IchBinLeoon/anisearch-discord-bot/main'
                                   '/anisearch/__init__.py') as response:
                github_version = str(re.findall("__version__ = '(.*)'", await response.text())[0])
                if github_version != anisearch.__version__:
                    logger.info('Update available! You are running version {}. Version {}'
                                ' is available at https://github.com/IchBinLeoon/anisearch-discord-bot.'
                                .format(anisearch.__version__, github_version))
                else:
                    logger.info('The bot is up to date')
    except Exception as exception:
        logger.error('An error occurred while checking for a newer version: {}'.format(exception))


def database_check():
    logger.info('Checking Database')
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        logger.info('Database connection is working properly')
    except Exception as exception:
        logger.exception(exception)
        logger.info('Cannot connect to Database')
        sys.exit()
    logger.info('Checking Tables')
    cur = db.cursor()
    cur.execute('SELECT EXISTS(SELECT * FROM information_schema.tables WHERE TABLE_NAME = %s)', ('guilds',))
    guilds_table = cur.fetchone()[0]
    if guilds_table:
        logger.info('Guilds Table exist')
    else:
        logger.info("Guilds Table doesn't exist")
        logger.info('Creating Guilds Table')
        cur.execute('CREATE TABLE guilds (id bigint, prefix VARCHAR (255))')
        logger.info('Guilds Table created')
    cur.execute('SELECT EXISTS(SELECT * FROM information_schema.tables WHERE TABLE_NAME = %s)', ('users',))
    users_table = cur.fetchone()[0]
    if users_table:
        logger.info('Users Table exist')
    else:
        logger.info("Users Table doesn't exist")
        logger.info('Creating Users Table')
        cur.execute('CREATE TABLE users (id bigint, anilist VARCHAR (255), myanimelist VARCHAR (255), kitsu '
                    'VARCHAR (255))')
        logger.info('Users Table created')
    db.commit()
    cur.close()
    db.close()
    logger.info('Database Check completed')


def start_bot():
    logger.info('Running Bot')
    try:
        bot = AniSearchBot()
        bot.run(config.TOKEN)
    except Exception as exception:
        logger.exception(exception)
        sys.exit()


if __name__ == '__main__':
    main()
