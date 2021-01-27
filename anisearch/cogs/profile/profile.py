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

from discord.ext import commands

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Profile(commands.Cog, name='Profile'):
    """Profile cog."""

    def __init__(self, bot: AniSearchBot):
        """Initializes the `Profile` cog."""
        self.bot = bot
