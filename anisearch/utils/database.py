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

log = logging.getLogger(__name__)


class DataBase:
    """
    Class for interacting with the Postgres database.

    Attributes:
        pool (psycopg2.pool.SimpleConnectionPool): A connection pool.
    """

    def __init__(self) -> None:
        """Initializes the DataBase class."""
        self.pool = psycopg2.pool.SimpleConnectionPool(5, 20, host=DB_HOST, dbname=DB_NAME,
                                                       user=DB_USER, password=BD_PASSWORD)

    def _connect(self):
        """Creates a connection with the Postgres database."""
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER,
                                password=BD_PASSWORD)
        return conn

    def close(self) -> None:
        """Closes all connections handled by the pool."""
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
            return 'as!'
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
                        'INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
                    conn.commit()
                    cur.execute(
                        'SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
                    prefix = cur.fetchone()[0]
                    log.info(f'Inserted prefix for guild {message.guild.id}.')
                    return prefix
        finally:
            self.pool.putconn(conn)

    def insert_prefix(self, guild: discord.Guild) -> None:
        """Inserts a new guild and the default prefix into the database.

        Args:
            guild (discord.Guild): A Discord guild.
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE guilds SET prefix = %s WHERE id = %s;', ('as!', guild.id,))
                cur.execute('INSERT INTO guilds (id, prefix) SELECT %s, %s WHERE NOT EXISTS '
                            '(SELECT 1 FROM guilds WHERE id = %s);', (guild.id, 'as!', guild.id, ))
                conn.commit()
                log.info(f'Inserted prefix for guild {guild.id}.')
        finally:
            self.pool.putconn(conn)

    def delete_prefix(self, guild: discord.Guild) -> None:
        """Deletes a guild from the database.

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

    def setup(self):
        """Sets up the database tables."""
        pass
