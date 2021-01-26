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
import time

import discord
from aiohttp import ClientSession
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, CommandError, Context, when_mentioned_or

from anisearch.config import OWNER_ID
from anisearch.utils.anilist import AniListClient
from anisearch.utils.animethemes import AnimeThemesClient
from anisearch.utils.database import DataBase

log = logging.getLogger(__name__)

initial_extensions = [
    'anisearch.cogs.search',
    'anisearch.cogs.help',
    'anisearch.cogs.theme',
    'anisearch.cogs.settings'
]


class AniSearchBot(AutoShardedBot):
    """A subclass of `discord.ext.commands.AutoShardedBot`."""

    def __init__(self) -> None:
        """Initializes the AniSearchBot."""
        intents = discord.Intents(messages=True, guilds=True, reactions=True)
        super().__init__(command_prefix=get_prefix, intents=intents, owner_id=int(OWNER_ID))
        self.start_time = time.time()
        self.db = DataBase()
        self.session = ClientSession(loop=self.loop)
        self.anilist = AniListClient(ClientSession(loop=self.loop))
        self.animethemes = AnimeThemesClient(ClientSession(loop=self.loop))
        self.load_cogs()

    def load_cogs(self) -> None:
        """Loads all cogs."""
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                log.exception(e)
        log.info(f'{len(self.cogs)}/{len(initial_extensions)} cogs loaded.')

    async def close(self):
        self.db.close()
        await self.anilist.close()
        await self.animethemes.close()
        if self.session is not None:
            await self.session.close()
        await super().close()

    async def on_ready(self) -> None:
        log.info(f'Logged in as {self.user}')
        log.info(f'Bot-Name: {self.user.name}')
        log.info(f'Bot-Discriminator: {self.user.discriminator}')
        log.info(f'Bot-ID: {self.user.id}')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='as!help'),
                                   status=discord.Status.online)
        log.info('Bot is ready.')

    async def on_connect(self) -> None:
        log.info('Connected to Discord.')

    async def on_disconnect(self) -> None:
        log.info('Disconnected from Discord.')

    async def on_command(self, ctx: Context) -> None:
        if isinstance(ctx.channel, discord.channel.DMChannel):
            log.info(
                f'Private Message - Author: {ctx.author} - Content: {ctx.message.content}')
        else:
            log.info(
                f'Server: {ctx.guild.name} - Author: {ctx.author} - Content: {ctx.message.content}')

    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info(f'Joined server {guild.name}.')
        self.db.insert_prefix(guild)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        log.info(f'Left server {guild.name}.')
        self.db.delete_prefix(guild)

    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        log.exception(error)


async def get_prefix(bot: AniSearchBot, message: discord.Message) -> when_mentioned_or():
    """
    Gets the command prefix of the bot for the current guild.

    Args:
        bot (AniSearchBot): The Discord bot.
        message (discord.Message): A Discord message.

    Returns:
        when_mentioned_or()
    """
    if isinstance(message.channel, discord.channel.DMChannel):
        return when_mentioned_or('as!')(bot, message)
    prefix = bot.db.get_prefix(message)
    return when_mentioned_or(prefix, 'as!')(bot, message)
