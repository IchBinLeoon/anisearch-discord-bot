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
from typing import Dict, Any, Union, List

import discord
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.cogs.search import Search
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, CRUNCHYROLL_LOGO, ANIMENEWSNETWORK_LOGO, \
    ANIMENEWSNETWORK_NEWS_FEED_ENDPOINT, CRUNCHYROLL_NEWS_FEED_ENDPOINT
from anisearch.utils.formatters import clean_html
from anisearch.utils.http import get
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.types import AniListMediaType

log = logging.getLogger(__name__)


class News(commands.Cog, name='News'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    async def scrape_animenewsnetwork(self, count: int) -> Union[List[Dict[str, Any]], None]:
        text = await get(ANIMENEWSNETWORK_NEWS_FEED_ENDPOINT, self.bot.session, res_method='text')
        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('item')
        if items:
            data = []
            for item in items:
                if len(data) >= count:
                    break
                feed = {
                    'title': item.find('title').text,
                    'link': item.find('guid').text,
                    'description': item.find('description').text,
                    'category': item.find('category').text if item.find('category') else None,
                    'date': item.find('pubdate').text
                }
                data.append(feed)
            return data
        return None

    async def scrape_crunchyroll(self, count: int) -> Union[List[Dict[str, Any]], None]:
        text = await get(CRUNCHYROLL_NEWS_FEED_ENDPOINT, self.bot.session, res_method='text')
        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('item')
        if items:
            data = []
            for item in items:
                if len(data) >= count:
                    break
                feed = {
                    'title': item.find('title').text,
                    'author': item.find('author').text,
                    'description': item.find('description').text,
                    'date': item.find('pubdate').text,
                    'link': item.find('guid').text
                }
                data.append(feed)
            return data
        return None

    @staticmethod
    async def get_aninews_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = discord.Embed(title=data.get('title'), url=data.get('link'), color=DEFAULT_EMBED_COLOR,
                              description=f'```{html.unescape(clean_html(data.get("description"))).rstrip()}```')

        category = None
        if data.get('category'):
            category = f' | {data.get("category")}'

        embed.set_author(name=f'Anime News Network News | {data.get("date").replace("-0500", "EST")}'
                              f'{category if data.get("category") else ""}', icon_url=ANIMENEWSNETWORK_LOGO)

        embed.set_footer(
            text=f'Provided by https://www.animenewsnetwork.com/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_crunchynews_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = discord.Embed(title=data.get('title'), url=data.get('link'), color=DEFAULT_EMBED_COLOR,
                              description=f'```{html.unescape(clean_html(data.get("description"))).rstrip()}```')

        embed.set_author(
            name=f'Crunchyroll News | {data.get("date")}', icon_url=CRUNCHYROLL_LOGO)

        embed.set_footer(
            text=f'Provided by https://www.crunchyroll.com/ • Page {page}/{pages}')

        return embed

    @commands.command(name='aninews', usage='aninews', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def aninews(self, ctx: Context):
        """Displays the latest anime news from Anime News Network."""
        async with ctx.channel.typing():
            try:
                data = await self.scrape_animenewsnetwork(15)
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
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The Anime News Network news could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='crunchynews', aliases=['crnews'], usage='crunchynews', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def crunchynews(self, ctx: Context):
        """Displays the latest anime news from Crunchyroll."""
        async with ctx.channel.typing():
            try:
                data = await self.scrape_crunchyroll(15)
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
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The Crunchyroll news could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='trending', aliases=['trend'], usage='trending <anime|manga>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def trending(self, ctx: Context, media: str):
        """Displays the current trending anime or manga on AniList."""
        async with ctx.channel.typing():
            if media.lower() == AniListMediaType.Anime.lower():
                type_ = AniListMediaType.Anime.upper()
            elif media.lower() == AniListMediaType.Manga.lower():
                type_ = AniListMediaType.Manga.upper()
            else:
                ctx.command.reset_cooldown(ctx)
                raise discord.ext.commands.BadArgument
            try:
                data = await self.bot.anilist.trending(page=1, perPage=10, type=type_, sort='TRENDING_DESC')
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(title=f'An error occurred while searching for the trending {type_.lower()}. '
                                            f'Try again.', color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, entry in enumerate(data):
                    try:
                        embed = await Search.get_media_embed(entry, page + 1, len(data))
                        if not isinstance(ctx.channel, discord.channel.DMChannel):
                            if is_adult(entry) and not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                              description=f'An error occurred while loading the embed for the '
                                                          f'{type_.lower()}.')
                        embed.set_footer(
                            text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'No trending {type_.lower()} found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
