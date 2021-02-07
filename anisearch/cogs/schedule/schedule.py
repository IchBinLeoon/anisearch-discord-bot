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
import logging
from typing import Dict, Any

import discord
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.formatters import format_media_type
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Schedule(commands.Cog, name='Schedule'):
    """
    Schedule cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Schedule` cog.
        """
        self.bot = bot

    @staticmethod
    async def get_next_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `next` embed.

        Args:
            data (dict): The data about the next airing anime episode.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
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

        embed.set_author(name='Next Airing Episode')

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_last_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `last` embed.

        Args:
            data (dict): The data about the recently aired anime episode.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
        if data.get('media').get('externalLinks'):
            for i in data.get('media').get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')

        date = datetime.datetime.utcfromtimestamp(data.get("airingAt")).strftime("%B %d, %Y - %H:%M")

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

        embed.set_author(name='Recently Aired Episode')

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @commands.command(name='next', usage='next', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def next(self, ctx: Context):
        """
        Displays the next airing anime episodes.
        """
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
                        if is_adult(anime.get('media')):
                            if not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the next airing episode.')
                        embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title=f'The next airing episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='last', usage='last', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def last(self, ctx: Context):
        """
        Displays the most recently aired anime episodes.
        """
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
                        if is_adult(anime.get('media')):
                            if not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the recently aired episode.')
                        embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The most recently aired episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
