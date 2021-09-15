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

import datetime
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
    ANIMENEWSNETWORK_NEWS_FEED_ENDPOINT, CRUNCHYROLL_NEWS_FEED_ENDPOINT, ANILIST_LOGO
from anisearch.utils.formatters import clean_html, format_media_type
from anisearch.utils.http import get
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.types import AniListMediaType

log = logging.getLogger(__name__)


class News(commands.Cog, name='News'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @staticmethod
    async def get_next_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(
                f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(
                    f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
        if data.get('media').get('externalLinks'):
            for i in data.get('media').get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')

        embed = discord.Embed(
            colour=DEFAULT_EMBED_COLOR,
            description=f'Episode **{data.get("episode")}** airing in '
                        f'**{str(datetime.timedelta(seconds=data.get("timeUntilAiring")))}**.\n\n**Type:** '
                        f'{format_media_type(data.get("media")["format"]) if data.get("media")["format"] else "N/A"}'
                        f'\n**Duration:** '
                        f'{str(data.get("media")["duration"]) + " min" if data.get("media")["duration"] else "N/A"}\n'
                        f'\n{" | ".join(sites) if len(sites) > 0 else ""}')

        if data.get('media')['title']['english'] is None or data.get('media')['title']['english'] \
                == data.get('media')['title']['romaji']:
            embed.title = data.get('media')['title']['romaji']
        else:
            embed.title = f'{data.get("media")["title"]["romaji"]} ({data.get("media")["title"]["english"]})'

        embed.set_author(name='Next Airing Episode', icon_url=ANILIST_LOGO)

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_last_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(
                f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(
                    f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
        if data.get('media').get('externalLinks'):
            for i in data.get('media').get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')

        date = datetime.datetime.utcfromtimestamp(
            data.get("airingAt")).strftime("%B %d, %Y - %H:%M")

        embed = discord.Embed(
            colour=DEFAULT_EMBED_COLOR,
            description=f'Episode **{data.get("episode")}** aired at **{str(date)}** UTC.\n\n**Type:** '
                        f'{format_media_type(data.get("media")["format"]) if data.get("media")["format"] else "N/A"}'
                        f'\n**Duration:** '
                        f'{str(data.get("media")["duration"]) + " min" if data.get("media")["duration"] else "N/A"}\n'
                        f'\n{" | ".join(sites) if len(sites) > 0 else ""}')

        if data.get('media')['title']['english'] is None or data.get('media')['title']['english'] \
                == data.get('media')['title']['romaji']:
            embed.title = data.get('media')['title']['romaji']
        else:
            embed.title = f'{data.get("media")["title"]["romaji"]} ({data.get("media")["title"]["english"]})'

        embed.set_author(name='Recently Aired Episode', icon_url=ANILIST_LOGO)

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

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

    @commands.command(name='next', usage='next', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def next(self, ctx: Context):
        """Displays the next airing anime episodes."""
        async with ctx.channel.typing():
            try:
                data = await self.bot.anilist.schedule(page=1, perPage=15, notYetAired=True, sort='TIME')
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(
                    title=f'An error occurred while searching for the next airing episodes. Try again.',
                    color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, anime in enumerate(data):
                    try:
                        embed = await self.get_next_embed(anime, page + 1, len(data))
                        if not isinstance(ctx.channel, discord.channel.DMChannel):
                            if is_adult(anime.get('media')) and not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the next airing episode.')
                        embed.set_footer(
                            text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The next airing episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='last', usage='last', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def last(self, ctx: Context):
        """Displays the most recently aired anime episodes."""
        async with ctx.channel.typing():
            try:
                data = await self.bot.anilist.schedule(page=1, perPage=15, notYetAired=False, sort='TIME_DESC')
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(
                    title=f'An error occurred while searching for the most recently aired episodes. Try again.',
                    color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, anime in enumerate(data):
                    try:
                        embed = await self.get_last_embed(anime, page + 1, len(data))
                        if not isinstance(ctx.channel, discord.channel.DMChannel):
                            if is_adult(anime.get('media')) and not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the recently aired episode.')
                        embed.set_footer(
                            text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The most recently aired episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

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


def setup(bot: AniSearchBot):
    bot.add_cog(News(bot))
    log.info('News cog loaded')


def teardown(bot: AniSearchBot):
    log.info('News cog unloaded')
