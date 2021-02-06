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

import discord
import psycopg2
import psycopg2.pool

from anisearch.config import BD_PASSWORD, DB_HOST, DB_NAME, DB_USER
from anisearch.utils.constants import DEFAULT_PREFIX

log = logging.getLogger(__name__)


class DataBase:
    """
    Class for interacting with the Postgres database.

    Attributes:
        pool (psycopg2.pool.SimpleConnectionPool): A connection pool.
    """

    def __init__(self) -> None:
        """
        Initializes the DataBase class.
        """
        self.pool = psycopg2.pool.SimpleConnectionPool(5, 20, host=DB_HOST, dbname=DB_NAME,
                                                       user=DB_USER, password=BD_PASSWORD)

    @staticmethod
    def _connect():
        """
        Creates a connection with the Postgres database.
        """
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER,
                                password=BD_PASSWORD)
        return conn

    def close(self) -> None:
        """
        Closes all connections handled by the pool.
        """
        self.pool.closeall()

    def get_prefix(self, message: discord.Message) -> str:
        """
        Gets the prefix for the current guild from the database.

        Args:
            message (discord.Message): A Discord message.

        Returns:
            prefix (str): Prefix for the current guild.
        """
        if isinstance(message.channel, discord.channel.DMChannel):
            return DEFAULT_PREFIX
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute('SELECT prefix FROM guilds WHERE id = %s;',
                                (message.guild.id,))
                    prefix = cur.fetchone()[0]
                    return prefix
                except TypeError:
                    cur.execute(
                        'INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, DEFAULT_PREFIX))
                    conn.commit()
                    cur.execute(
                        'SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                    prefix = cur.fetchone()[0]
                    log.info(f'Inserted prefix for guild {message.guild.id}.')
                    return prefix
        finally:
            self.pool.putconn(conn)

    def insert_prefix(self, guild: discord.Guild) -> None:
        """
        Inserts a new guild and the default prefix into the database.

        Args:
            guild (discord.Guild): A Discord guild.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE guilds SET prefix = %s WHERE id = %s;', (DEFAULT_PREFIX, guild.id,))
                cur.execute('INSERT INTO guilds (id, prefix) SELECT %s, %s WHERE NOT EXISTS '
                            '(SELECT 1 FROM guilds WHERE id = %s);', (guild.id, DEFAULT_PREFIX, guild.id,))
                conn.commit()
                log.info(f'Inserted prefix for guild {guild.id}.')
        finally:
            self.pool.putconn(conn)

    def delete_prefix(self, guild: discord.Guild) -> None:
        """
        Deletes a guild from the database.

        Args:
            guild (discord.Guild): A Discord guild.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM guilds WHERE id = %s;', (guild.id,))
                conn.commit()
                log.info(f'Deleted prefix for guild {guild.id}.')
        finally:
            self.pool.putconn(conn)

    def update_prefix(self, message: discord.Message, prefix: str) -> None:
        """
        Updates the prefix from a guild in the database.

        Args:
            message (discord.Message): A Discord message.
            prefix (str): The new prefix.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('UPDATE guilds SET prefix = %s WHERE id = %s;',
                            (prefix, message.guild.id,))
                cur.execute('SELECT prefix FROM guilds WHERE id = %s;',
                            (message.guild.id,))
                prefix = cur.fetchone()[0]
                conn.commit()
                log.info(
                    f'Changed prefix for guild {message.guild.id} to `{prefix}`.')
        finally:
            self.pool.putconn(conn)

    def insert_profile(self, site: str, username: str, id_: int) -> None:
        """
        Inserts a profile of a user into the database.

        Args:
            site (str): The anime tracking site (`anilist`, `myanimelist`, `kitsu`).
            username (str): The profile name.
            id_ (int): The ID of the discord user.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                if site == 'anilist':
                    cur.execute('UPDATE users SET anilist = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, anilist) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                elif site == 'myanimelist':
                    cur.execute('UPDATE users SET myanimelist = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, myanimelist) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                elif site == 'kitsu':
                    cur.execute('UPDATE users SET kitsu = %s WHERE id = %s;', (username, id_,))
                    cur.execute('INSERT INTO users (id, kitsu) SELECT %s, %s WHERE NOT EXISTS '
                                '(SELECT 1 FROM users WHERE id = %s);', (id_, username, id_,))
                conn.commit()
                log.info(f'Set {site} profile for user {id_} to `{username}`.')
        finally:
            self.pool.putconn(conn)

    def select_profile(self, site: str, id_: int) -> None:
        """
        Selects a profile of a user from the database.

        Args:
            site (str): The anime tracking site (`anilist`, `myanimelist`, `kitsu`).
            id_ (int): The ID of the discord user.

        Returns:
            profile (str): The requested profile.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                try:
                    if site == 'anilist':
                        cur.execute('SELECT anilist FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    elif site == 'myanimelist':
                        cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    elif site == 'kitsu':
                        cur.execute('SELECT kitsu FROM users WHERE id = %s;', (id_,))
                        profile = cur.fetchone()[0]
                    return profile
                except TypeError:
                    return None
        finally:
            self.pool.putconn(conn)

    def delete_user(self, id_: int) -> None:
        """
        Deletes a user from the database.

        Args:
            id_ (int): The ID of the discord user.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM users WHERE id = %s;', (id_,))
                conn.commit()
                log.info(f'Removed all profiles for user {id_}.')
        finally:
            self.pool.putconn(conn)

    def setup(self):
        """
        Sets up the database tables.
        """
