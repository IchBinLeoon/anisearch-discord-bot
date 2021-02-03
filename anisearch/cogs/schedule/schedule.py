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

import discord
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.formats import get_media_title, format_media_type
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

    @commands.command(name='next', usage='next', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def next(self, ctx: Context):
        """
        Displays the next airing anime episodes.
        """
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

                    sites = []
                    if anime.get('media').get('siteUrl'):
                        sites.append(f'[Anilist]({anime.get("media").get("siteUrl")})')
                    if anime.get('media').get('idMal'):
                        sites.append(
                            f'[MyAnimeList](https://myanimelist.net/anime/{str(anime.get("media").get("idMal"))})')
                    if anime.get('media').get('trailer'):
                        if anime.get('media').get('trailer')['site'] == 'youtube':
                            trailer_site = 'https://www.youtube.com/watch?v=' + \
                                           anime.get('media').get('trailer')['id']
                            sites.append('[Trailer]({})'.format(trailer_site))
                    if anime.get('media').get('externalLinks'):
                        for i in anime.get('media').get('externalLinks'):
                            sites.append('[{}]({})'.format(i['site'], i['url']))
                    if len(sites) > 0:
                        sites = ' | '.join(sites)

                    embed = discord.Embed(
                        title=get_media_title(anime.get('media')['title']),
                        colour=DEFAULT_EMBED_COLOR,
                        description=
                        f'Episode **{anime.get("episode")}** airing in '
                        f'**{str(datetime.timedelta(seconds=anime.get("timeUntilAiring")))}**.\n'
                        f'\n'
                        f'**Type:** '
                        f'{format_media_type(anime.get("media")["format"]) if anime.get("media")["format"] else "N/A"}'
                        f'\n'
                        f'**Duration:** '
                        f'{str(anime.get("media")["duration"]) + " min" if anime.get("media")["duration"] else "N/A"}\n'
                        f'\n'
                        f'{sites}'
                    )

                    embed.set_author(name='Next Airing Episode')
                    if anime.get('media').get('coverImage').get('large'):
                        embed.set_thumbnail(url=anime.get('media')['coverImage']['large'])
                    embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    if is_adult(anime.get('media')):
                        if not ctx.channel.is_nsfw():
                            embed = discord.Embed(
                                title='Error',
                                color=ERROR_EMBED_COLOR,
                                description=f'Adult content. No NSFW channel.')
                            embed.set_footer(
                                text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    embeds.append(embed)

                except Exception as e:
                    log.exception(e)

                    embed = discord.Embed(
                        title='Error',
                        description=f'An error occurred while loading the embed for the next airing episode.',
                        color=ERROR_EMBED_COLOR)
                    embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    embeds.append(embed)

            menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
            await menu.start(ctx)

        else:
            embed = discord.Embed(
                title=f'The next airing episodes could not be found.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    @commands.command(name='last', usage='last', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def last(self, ctx: Context):
        """
        Displays the most recently aired anime episodes.
        """
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

                    sites = []
                    if anime.get('media').get('siteUrl'):
                        sites.append(f'[Anilist]({anime.get("media").get("siteUrl")})')
                    if anime.get('media').get('idMal'):
                        sites.append(
                            f'[MyAnimeList](https://myanimelist.net/anime/{str(anime.get("media").get("idMal"))})')
                    if anime.get('media').get('trailer'):
                        if anime.get('media').get('trailer')['site'] == 'youtube':
                            trailer_site = 'https://www.youtube.com/watch?v=' + \
                                           anime.get('media').get('trailer')['id']
                            sites.append('[Trailer]({})'.format(trailer_site))
                    if anime.get('media').get('externalLinks'):
                        for i in anime.get('media').get('externalLinks'):
                            sites.append('[{}]({})'.format(i['site'], i['url']))
                    if len(sites) > 0:
                        sites = ' | '.join(sites)

                    date = datetime.datetime.utcfromtimestamp(anime.get("airingAt")).strftime("%B %d, %Y - %H:%M")

                    embed = discord.Embed(
                        title=get_media_title(anime.get('media')['title']),
                        colour=DEFAULT_EMBED_COLOR,
                        description=
                        f'Episode **{anime.get("episode")}** aired at **{str(date)}** UTC.\n'
                        f'\n'
                        f'**Type:** '
                        f'{format_media_type(anime.get("media")["format"]) if anime.get("media")["format"] else "N/A"}'
                        f'\n'
                        f'**Duration:** '
                        f'{str(anime.get("media")["duration"]) + " min" if anime.get("media")["duration"] else "N/A"}\n'
                        f'\n'
                        f'{sites}'
                    )

                    embed.set_author(name='Recently Aired Episode')
                    if anime.get('media').get('coverImage').get('large'):
                        embed.set_thumbnail(url=anime.get('media')['coverImage']['large'])
                    embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    if is_adult(anime.get('media')):
                        if not ctx.channel.is_nsfw():
                            embed = discord.Embed(
                                title='Error',
                                color=ERROR_EMBED_COLOR,
                                description=f'Adult content. No NSFW channel.')
                            embed.set_footer(
                                text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    embeds.append(embed)

                except Exception as e:
                    log.exception(e)

                    embed = discord.Embed(
                        title='Error',
                        description=f'An error occurred while loading the embed for the recently aired episode.',
                        color=ERROR_EMBED_COLOR)
                    embed.set_footer(text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                    embeds.append(embed)

            menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
            await menu.start(ctx)

        else:
            embed = discord.Embed(
                title=f'The most recently aired episodes could not be found.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
