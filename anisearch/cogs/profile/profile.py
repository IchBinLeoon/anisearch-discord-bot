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
from typing import Optional

from discord.ext import commands
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Profile(commands.Cog, name='Profile'):
    """Profile cog."""

    def __init__(self, bot: AniSearchBot):
        """Initializes the `Profile` cog."""
        self.bot = bot

    @commands.command(name='anilist', aliases=['al'], usage='anilist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anilist(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given AniList profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            pass

    @commands.command(name='myanimelist', aliases=['mal'], usage='myanimelist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def myanimelist(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given MyAnimeList profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            pass

    @commands.command(name='kitsu', aliases=['k', 'kit'], usage='kitsu [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kitsu(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given Kitsu profile such as anime stats, manga stats and favorites!"""
        async with ctx.channel.typing():
            pass

    @commands.command(name='setprofile', aliases=['set'], usage='setprofile <al|mal|kitsu> <username>',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def setprofile(self, ctx: Context, site: Optional[str] = None, username: Optional[str] = None):
        """Sets an AniList, MyAnimeList or Kitsu profile."""
        async with ctx.channel.typing():
            pass

    @commands.command(name='remove', aliases=['rm'], usage='remove', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def remove(self, ctx: Context):
        """Removes the set AniList, MyAnimeList and Kitsu profile."""
        async with ctx.channel.typing():
            pass
