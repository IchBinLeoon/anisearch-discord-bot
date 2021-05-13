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

from anisearch.bot import AniSearchBot
from anisearch.cogs.themes.themes import Themes

log = logging.getLogger(__name__)


def setup(bot: AniSearchBot):
    """Sets up the Themes cog."""
    bot.add_cog(Themes(bot))
    log.info('Themes cog loaded.')
