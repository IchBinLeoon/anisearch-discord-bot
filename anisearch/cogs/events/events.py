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

import dbl
from discord.ext import commands
from anisearch import config
from anisearch.utils.logger import logger


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.token = config.TOPGG_TOKEN
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        logger.info('TopGG server count posted ({})'.format(self.dblpy.guild_count()))
