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

from discord.ext import commands, ipc
from discord.ext.ipc.server import IpcServerResponse

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Ipc(commands.Cog, name='Ipc'):
    """
    Ipc cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Ipc` cog.
        """
        self.bot = bot

    @ipc.server.route()
    async def get_guild_count(self, data: IpcServerResponse):
        """
        Returns the bot guild count.
        """
        return str(self.bot.get_guild_count())

    @ipc.server.route()
    async def get_user_count(self, data: IpcServerResponse):
        """
        Returns the bot user count.
        """
        return str(self.bot.get_user_count())

    @ipc.server.route()
    async def get_channel_count(self, data: IpcServerResponse):
        """
        Returns the bot channel count.
        """
        return str(self.bot.get_channel_count())

    @ipc.server.route()
    async def get_uptime(self, data: IpcServerResponse):
        """
        Returns the bot uptime.
        """
        return str(self.bot.get_uptime())

    @ipc.server.route()
    async def get_shard_count(self, data: IpcServerResponse):
        """
        Returns the bot shard count.
        """
        return str(self.bot.shard_count)
