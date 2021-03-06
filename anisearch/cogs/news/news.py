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

import html
import logging
from typing import Dict, Any

import discord
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, CRUNCHYROLL_LOGO, ANIMENEWSNETWORK_LOGO
from anisearch.utils.formatters import clean_html
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class News(commands.Cog, name='News'):
    """
    News cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `News` cog.
        """
        self.bot = bot

    @staticmethod
    async def get_aninews_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `aninews` embed.

        Args:
            data (dict): The data about the anime news.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(title=data.get('title'), url=data.get('link'), color=DEFAULT_EMBED_COLOR,
                              description=f'```{html.unescape(clean_html(data.get("description"))).rstrip()}```')

        category = None
        if data.get('category'):
            category = f' | {data.get("category")}'

        embed.set_author(name=f'Anime News Network News | {data.get("date").replace("-0500", "EST")}'
                              f'{category if data.get("category") else ""}', icon_url=ANIMENEWSNETWORK_LOGO)

        embed.set_footer(text=f'Provided by https://www.animenewsnetwork.com/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_crunchynews_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `crunchynews` embed.

        Args:
            data (dict): The data about the anime news.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(title=data.get('title'), url=data.get('link'), color=DEFAULT_EMBED_COLOR,
                              description=f'```{html.unescape(clean_html(data.get("description"))).rstrip()}```')

        embed.set_author(name=f'Crunchyroll News | {data.get("date")}', icon_url=CRUNCHYROLL_LOGO)

        embed.set_footer(text=f'Provided by https://www.crunchyroll.com/ • Page {page}/{pages}')

        return embed

    @commands.command(name='aninews', usage='aninews', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def aninews(self, ctx: Context):
        """
        Displays the latest anime news from Anime News Network.
        """
        async with ctx.channel.typing():
            try:
                data = await self.bot.animenewsnetwork.news(count=15)
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(
                    title=f'An error occurred while searching for the Anime News Network news. Try again.',
                    color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, news in enumerate(data):
                    try:
                        embed = await self.get_aninews_embed(news, page + 1, len(data))
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the Anime News Network news.')
                        embed.set_footer(
                            text=f'Provided by https://www.animenewsnetwork.com/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title=f'The Anime News Network news could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='crunchynews', aliases=['crnews'], usage='crunchynews', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def crunchynews(self, ctx: Context):
        """
        Displays the latest anime news from Crunchyroll.
        """
        async with ctx.channel.typing():
            try:
                data = await self.bot.crunchyroll.news(count=15)
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(title=f'An error occurred while searching for the Crunchyroll news. Try again.',
                                      color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, news in enumerate(data):
                    try:
                        embed = await self.get_crunchynews_embed(news, page + 1, len(data))
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the Crunchyroll news.')
                        embed.set_footer(
                            text=f'Provided by https://www.crunchyroll.com/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title=f'The Crunchyroll news could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
