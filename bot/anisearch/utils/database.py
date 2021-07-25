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
from typing import Union

import discord
import psycopg2
import psycopg2.pool

from anisearch.config import DB_PASSWORD, DB_HOST, DB_NAME, DB_USER, DB_PORT
from anisearch.utils.constants import DEFAULT_PREFIX

log = logging.getLogger(__name__)


class DataBase:
    """Class for interacting with the Postgres database."""

    def __init__(self) -> None:
        self.pool = psycopg2.pool.SimpleConnectionPool(5, 20, host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER,
                                                       password=DB_PASSWORD)

    @staticmethod
    def _connect():
        """Creates a connection with the Postgres database."""
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        return conn

    def close(self) -> None:
        """Closes all connections handled by the pool."""
        self.pool.closeall()

    def get_prefix(self, message: discord.Message) -> str:
        """Gets the prefix for the current guild from the database."""
        if isinstance(message.channel, discord.channel.DMChannel):
            return DEFAULT_PREFIX
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        'SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                    prefix = cur.fetchone()[0]
                    return prefix
                except TypeError:
                    cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)',
                                (message.guild.id, DEFAULT_PREFIX))
                    conn.commit()
                    cur.execute(
                        'SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                    prefix = cur.fetchone()[0]
                    log.info(
                        f'Inserted prefix for guild {message.guild.name} [{message.guild.id}].')
                    return prefix
        finally:
            self.pool.putconn(conn)

    def insert_prefix(self, guild: discord.Guild) -> None:
        """Inserts a new guild and the default prefix into the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE guilds SET prefix = %s WHERE id = %s;', (DEFAULT_PREFIX, guild.id,))
                cur.execute('INSERT INTO guilds (id, prefix) SELECT %s, %s WHERE NOT EXISTS '
                            '(SELECT 1 FROM guilds WHERE id = %s);', (guild.id, DEFAULT_PREFIX, guild.id,))
                conn.commit()
                log.info(
                    f'Inserted prefix for guild {guild.name} [{guild.id}].')
        finally:
            self.pool.putconn(conn)

    def delete_prefix(self, guild: discord.Guild) -> None:
        """Deletes a guild from the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM guilds WHERE id = %s;', (guild.id,))
                conn.commit()
                log.info(
                    f'Deleted prefix for guild {guild.name} [{guild.id}].')
        finally:
            self.pool.putconn(conn)

    def update_prefix(self, message: discord.Message, prefix: str) -> None:
        """Updates the prefix from a guild in the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE guilds SET prefix = %s WHERE id = %s;', (prefix, message.guild.id,))
                cur.execute(
                    'SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                prefix = cur.fetchone()[0]
                conn.commit()
                log.info(
                    f'Changed prefix for guild {message.guild.name} [{message.guild.id}] to {prefix}.')
        finally:
            self.pool.putconn(conn)

    def insert_profile(self, site: str, username: str, id_: int) -> None:
        """Inserts a profile of a user into the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                if site == 'anilist':
                    cur.execute(
                        'UPDATE users SET anilist = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, anilist) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                elif site == 'myanimelist':
                    cur.execute(
                        'UPDATE users SET myanimelist = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, myanimelist) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                elif site == 'kitsu':
                    cur.execute(
                        'UPDATE users SET kitsu = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, kitsu) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                conn.commit()
                log.info(f'Added {site} profile for user {id_} to {username}.')
        finally:
            self.pool.putconn(conn)

    def select_profile(self, site: str, id_: int) -> Union[str, None]:
        """Selects a profile of a user from the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                try:
                    if site == 'anilist':
                        cur.execute(
                            'SELECT anilist FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    elif site == 'myanimelist':
                        cur.execute(
                            'SELECT myanimelist FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    elif site == 'kitsu':
                        cur.execute(
                            'SELECT kitsu FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    return profile
                except TypeError:
                    return None
        finally:
            self.pool.putconn(conn)

    def delete_user(self, id_: int) -> None:
        """Deletes a user from the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM users WHERE id = %s;', (id_,))
                conn.commit()
                log.info(f'Removed all profiles for user {id_}.')
        finally:
            self.pool.putconn(conn)

    def set_channel(self, channel_id: int, guild: discord.Guild) -> None:
        """Sets the channel for the matching guild in the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE guilds SET channel = %s WHERE id = %s;', (channel_id, guild.id,))
                cur.execute(
                    'SELECT channel FROM guilds WHERE id = %s;', (guild.id,))
                channel_id = cur.fetchone()[0]
                conn.commit()
                log.info(
                    f'Set channel for guild {guild.name} [{guild.id}] to {channel_id}.')
        finally:
            self.pool.putconn(conn)

    def get_channel(self, guild: discord.Guild) -> Union[int, None]:
        """Gets the channel for the current guild from the database."""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        'SELECT channel FROM guilds WHERE id = %s;', (guild.id,))
                    channel = cur.fetchone()[0]
                    return channel
                except TypeError:
                    return None
        finally:
            self.pool.putconn(conn)
