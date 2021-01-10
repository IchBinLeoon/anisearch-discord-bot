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

import discord
import psycopg2
from discord.ext.commands import when_mentioned_or
from anisearch import config
from anisearch.utils.logger import logger


def get_command_prefix(self, message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return when_mentioned_or('as!')(self, message)
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        try:
            cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
            prefix = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
            return when_mentioned_or(prefix, 'as!')(self, message)
        except TypeError:
            cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
            cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
            prefix = cur.fetchone()[0]
            db.commit()
            cur.close()
            db.close()
            logger.info('Changed Prefix for Guild {} to {}'.format(message.guild.id, prefix))
            return when_mentioned_or(prefix, 'as!')(self, message)
    except Exception as exception:
        logger.exception(exception)
        return when_mentioned_or('as!')(self, message)


def select_prefix(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return 'as!'
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return prefix
    except Exception as exception:
        logger.exception(exception)


def insert_prefix(guild):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (guild.id, 'as!'))
        db.commit()
        cur.close()
        db.close()
        logger.info('Set Prefix for Guild {}'.format(guild.id))
    except Exception as exception:
        logger.exception(exception)


def delete_prefix(guild):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('DELETE FROM guilds WHERE id = %s', (guild.id,))
        db.commit()
        cur.close()
        db.close()
        logger.info('Deleted Prefix for Guild {}'.format(guild.id))
    except Exception as exception:
        logger.exception(exception)


def change_prefix(ctx, prefix):
    try:
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        cur.execute('UPDATE guilds SET prefix = %s WHERE id = %s;', (prefix, ctx.guild.id,))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
        prefix_new = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        logger.info('Changed Prefix for Guild {} to {}'.format(ctx.guild.id, prefix))
        return prefix_new
    except Exception as exception:
        logger.exception(exception)
