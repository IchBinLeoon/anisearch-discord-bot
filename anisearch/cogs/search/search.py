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
import random
from typing import Union, List, Dict, Any, Optional

import discord
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.formats import get_media_title, get_media_stats, format_description, format_date, \
    get_char_staff_name, format_media_type
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Search(commands.Cog, name='Search'):
    """Search cog."""

    def __init__(self, bot: AniSearchBot):
        """Initializes the `Search` cog."""
        self.bot = bot

    async def anilist_search(self, search: str, type_: str) -> Union[List[Embed], None]:
        """
        Returns a list of Discord embeds with the retrieved anilist data about the searched entry.

        Args:
            search (str): The entry to be searched for.
            type_ (str): The type to be searched for (`anime`, `manga`, `character`, `staff`, `studio`).

        Returns:
            list (Embed): A list of discord embeds.
            None: If no entries were found.
        """
        embeds = []
        data = None

        try:
            if type_ == 'anime':
                data = await self.bot.anilist.media(search=search, page=1, perPage=15, type=type_.upper())
            elif type_ == 'manga':
                data = await self.bot.anilist.media(search=search, page=1, perPage=15, type=type_.upper())
            elif type_ == 'character':
                data = await self.bot.anilist.character(search=search, page=1, perPage=15)
            elif type_ == 'staff':
                data = await self.bot.anilist.staff(search=search, page=1, perPage=15)
            elif type_ == 'studio':
                data = await self.bot.anilist.studio(search=search, page=1, perPage=15)

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching for the {type_} `{search}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:
            for page, entry in enumerate(data):

                embed = None

                try:
                    if type_ == 'anime':
                        embed = self.get_media_embed(entry, page + 1, len(data))
                    elif type_ == 'manga':
                        embed = self.get_media_embed(entry, page + 1, len(data))
                    elif type_ == 'character':
                        embed = self.get_character_embed(entry, page + 1, len(data))
                    elif type_ == 'staff':
                        embed = self.get_staff_embed(entry, page + 1, len(data))
                    elif type_ == 'studio':
                        embed = self.get_studio_embed(entry, page + 1, len(data))

                except Exception as e:
                    log.exception(e)

                    embed = discord.Embed(
                        title='Error',
                        color=ERROR_EMBED_COLOR,
                        description=f'An error occurred while loading the embed for the {type_}.')
                    embed.set_footer(
                        text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                embeds.append(embed)

            return embeds
        return None

    async def anilist_random(self, search: str, type_: str, format_in: List[str]) -> Union[Embed, None]:
        """
        Returns a Discord embed with the retrieved anilist data about a random media of a specified genre.

        Args:
            search (str): The media genre to be searched for.
            type_ (str): The media search type (`anime`, `manga`).
            format_in: The media format. (`TV`, `MOVIE`, `MANGA`)

        Returns:
            Embed: A discord embed.
            None: If no entry was found.
        """
        try:

            data = await self.bot.anilist.genre(genre=search, page=1, perPage=1, type=type_.upper(),
                                                format_in=format_in)

            if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:
                page = random.randrange(1, data.get('data')['Page']['pageInfo']['lastPage'])
                data = await self.bot.anilist.genre(genre=search, page=page, perPage=1, type=type_.upper(),
                                                    format_in=format_in)

            else:

                data = await self.bot.anilist.tag(tag=search, page=1, perPage=1, type=type_.upper(),
                                                  format_in=format_in)

                if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:
                    page = random.randrange(1, data.get('data')['Page']['pageInfo']['lastPage'])
                    data = await self.bot.anilist.tag(tag=search, page=page, perPage=1, type=type_.upper(),
                                                      format_in=format_in)
                else:
                    return None

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching for an {type_} with the genre `{search}`.',
                color=ERROR_EMBED_COLOR)

            return embed

        if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:

            try:
                embed = self.get_media_embed(data.get('data')['Page']['media'][0])

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title=f'An error occurred while searching for an {type_} with the genre `{search}`.',
                    color=ERROR_EMBED_COLOR)

            return embed

        return None

    @staticmethod
    def get_media_embed(data: Dict[str, Any], page: Optional[int] = None, pages: Optional[int] = None) -> Embed:
        """
        Returns the `media` embed.

        Args:
            data (dict): The data about the anime.
            page (int, optional): The current page.
            pages (page, optional): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(
            title=get_media_title(data.get('title')),
            description=format_description(data.get('description'), 400) if data.get('description')
            else 'N/A',
            colour=int('0x' + data.get('coverImage')['color'].replace('#', ''), 0) if data.get('coverImage')['color']
            else DEFAULT_EMBED_COLOR
        )

        if data.get('coverImage')['large']:
            embed.set_thumbnail(url=data.get('coverImage')['large'])

        if data.get('bannerImage'):
            embed.set_image(url=data.get('bannerImage'))

        embed.set_author(name=get_media_stats(data.get('format'), data.get('type'), data.get('status'),
                                              data.get('meanScore')))

        if data.get('type') == 'ANIME':
            if data.get('status') == 'RELEASING':
                try:
                    if data.get('nextAiringEpisode')['episode']:
                        aired_episodes = str(
                            data.get('nextAiringEpisode')['episode'] - 1)
                        next_episode_time = 'N/A'
                        if data.get('nextAiringEpisode')['timeUntilAiring']:
                            seconds = data.get('nextAiringEpisode')[
                                'timeUntilAiring']
                            next_episode_time = str(
                                datetime.timedelta(seconds=seconds))
                        embed.add_field(name='Aired Episodes', value=f'{aired_episodes} (Next in {next_episode_time})',
                                        inline=True)
                except TypeError:
                    embed.add_field(name='Episodes', value='N/A', inline=True)
            elif data.get('episodes'):
                embed.add_field(name='Episodes', value=data.get(
                    'episodes'), inline=True)

        elif data.get('type') == 'MANGA':
            embed.add_field(name='Chapters', value=data.get(
                'chapters') if data.get('chapters') else 'N/A', inline=True)
            embed.add_field(name='Volumes', value=data.get(
                'volumes') if data.get('volumes') else 'N/A', inline=True)
            embed.add_field(name='Source', value=data.get('source').replace('_', ' ').title() if data.get('source') else
                            'N/A', inline=True)

        date_name = 'Released'
        if data.get('type') == 'ANIME':
            date_name = 'Aired'
        elif data.get('type') == 'MANGA':
            date_name = 'Published'
        if data.get('startDate')['day']:
            try:
                start_date = format_date(data.get('startDate')['day'], data.get('startDate')['month'],
                                         data.get('startDate')['year'])
                end_date = '?'
                if data.get('endDate')['day']:
                    end_date = format_date(data.get('endDate')['day'], data.get('endDate')['month'],
                                           data.get('endDate')['year'])
                embed.add_field(name=date_name, value='{} to {}'.format(
                    start_date, end_date), inline=False)
            except TypeError:
                embed.add_field(name=date_name, value='N/A', inline=False)
        else:
            embed.add_field(name=date_name, value='N/A', inline=False)

        if data.get('type') == 'ANIME':
            duration = 'N/A'
            if data.get('duration'):
                duration = str(data.get(
                    'duration')) + ' {}'.format('min' if data.get('episodes') == 1 else 'min each')
            embed.add_field(name='Duration', value=duration, inline=True)
            embed.add_field(name='Source', value=data.get('source').replace('_', ' ').title() if data.get('source') else
                            'N/A', inline=True)
            try:
                studio = data.get('studios')['nodes'][0]['name']
            except IndexError:
                studio = 'N/A'
            embed.add_field(name='Studio', value=studio, inline=True)

        if data.get('synonyms'):
            embed.add_field(name='Synonyms', value=', '.join(
                data.get('synonyms')), inline=False)

        if data.get('genres'):
            embed.add_field(name='Genres', value=', '.join(
                data.get('genres')), inline=False)

        external_sites = []
        if data.get('trailer'):
            if data.get('trailer')['site'] == 'youtube':
                trailer_site = 'https://www.youtube.com/watch?v=' + \
                               data.get('trailer')['id']
                external_sites.append('[Trailer]({})'.format(trailer_site))
        if data.get('externalLinks'):
            for i in data.get('externalLinks'):
                external_sites.append('[{}]({})'.format(i['site'], i['url']))
        if len(external_sites) > 1:
            external_name = 'External sites'
            if data.get('type') == 'ANIME':
                external_name = 'Streaming and external sites'
            embed.add_field(name=external_name, value=' | '.join(
                external_sites), inline=False)

        sites = []
        if data.get('siteUrl'):
            sites.append('[Anilist]({})'.format(data.get('siteUrl')))
            embed.url = data.get('siteUrl')
        if data.get('idMal'):
            sites.append(
                '[MyAnimeList](https://myanimelist.net/anime/{})'.format(str(data.get('idMal'))))
        if len(sites) > 0:
            embed.add_field(name='Find out more',
                            value=' | '.join(sites), inline=False)

        if page is not None and pages is not None:
            embed.set_footer(
                text=f'Provided by https://anilist.co/ • Page {page}/{pages}')
        else:
            embed.set_footer(text=f'Provided by https://anilist.co/')

        return embed

    @staticmethod
    def get_character_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `character` embed.

        Args:
            data (dict): The data about the character.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(
            color=DEFAULT_EMBED_COLOR,
            description=format_description(data.get('description'), 1000) if data.get('description') else 'N/A',
            title=get_char_staff_name(data.get('name'))
        )

        if data.get('image')['large']:
            embed.set_thumbnail(url=data.get('image')['large'])

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if data.get('name')['alternative'] != ['']:
            embed.add_field(name='Synonyms', value=', '.join(
                data.get('name')['alternative']), inline=False)

        if data.get('media')['nodes']:
            media = []
            for x in data.get('media')['nodes']:
                media_name = '[{}]({})'.format(
                    [x][0]['title']['romaji'], [x][0]['siteUrl'])
                media.append(media_name)
            if len(media) > 5:
                media = media[0:5]
                media[4] = media[4] + '...'
            embed.add_field(name='Appearances',
                            value=' | '.join(media), inline=False)
        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    def get_staff_embed(data: Dict[str, Any], page: Optional[int], pages: Optional[int]) -> Embed:
        """
        Returns the `staff` embed.

        Args:
            data (dict): The data about the staff.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(
            title=get_char_staff_name(data.get('name')),
            description=format_description(data.get('description'), 1000) if data.get('description') else 'N/A',
            color=DEFAULT_EMBED_COLOR
        )

        if data.get('image')['large']:
            embed.set_thumbnail(url=data.get('image')['large'])

        if data.get('name')['native'] is None:
            embed.title = data.get('name')['full']

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if data.get('staffMedia')['nodes']:
            staff_roles = []
            for x in data.get('staffMedia')['nodes']:
                media_name = '[{}]({})'.format(
                    [x][0]['title']['romaji'], [x][0]['siteUrl'])
                staff_roles.append(media_name)
            if len(staff_roles) > 5:
                staff_roles = staff_roles[0:5]
                staff_roles[4] = staff_roles[4] + '...'
            embed.add_field(name='Staff Roles', value=' | '.join(
                staff_roles), inline=False)

        if data.get('characters')['nodes']:
            characters = []
            for x in data.get('characters')['nodes']:
                character_name = '[{}]({})'.format([x][0]['name']['full'],
                                                   [x][0]['siteUrl'])
                characters.append(character_name)
            if len(characters) > 5:
                characters = characters[0:5]
                characters[4] = characters[4] + '...'
            embed.add_field(name='Character Roles',
                            value=' | '.join(characters), inline=False)

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    def get_studio_embed(data: Dict[str, Any], page: Optional[int], pages: Optional[int]) -> Embed:
        """
        Returns the `studio` embed.

        Args:
            data (dict): The data about the studio.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(
            color=DEFAULT_EMBED_COLOR,
            title=data.get('name')
        )

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if data.get('media')['nodes']:
            medias = []
            for x in data.get('media')['nodes']:
                media_name = [x][0]['title']['romaji']
                media_link = [x][0]['siteUrl']
                try:
                    media_type = format_media_type([x][0]['format'])
                except KeyError:
                    media_type = 'N/A'
                media_count = [x][0]['episodes']
                list_object = '[{}]({}) - Type: {} - Episodes: {}'.format(media_name, media_link,
                                                                          media_type, media_count)
                medias.append(list_object)
            if len(medias) > 10:
                medias = medias[0:10]
                medias[9] = medias[9] + '...'
            embed.add_field(name='Most Popular Productions',
                            value='\n'.join(medias), inline=False)

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @commands.command(name='anime', aliases=['a', 'ani'], usage='anime <title>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def anime(self, ctx: Context, *, title: str):
        """Searches for an anime with the given title and displays information about the search results such as type, status, episodes, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(title, 'anime')
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The anime `{title}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='manga', aliases=['m'], usage='manga <title>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def manga(self, ctx: Context, *, title: str):
        """Searches for a manga with the given title and displays information about the search results such as type, status, chapters, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(title, 'manga')
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The manga `{title}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='character', aliases=['c', 'char'], usage='character <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def character(self, ctx: Context, *, name: str):
        """Searches for a character with the given name and displays information about the search results such as description, synonyms, and appearances!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(name, 'character')
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The character `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='staff', usage='staff <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def staff(self, ctx: Context, *, name: str):
        """Searches for a staff with the given name and displays information about the search results such as description, staff roles, and character roles!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(name, 'staff')
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The staff `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='studio', usage='studio <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def studio(self, ctx: Context, *, name: str):
        """Searches for a studio with the given name and displays information about the search results such as the studio productions!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(name, 'studio')
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The studio `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='random', aliases=['r'], usage='random <anime|manga> <genre>', ignore_extra=False)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def random(self, ctx: Context, media: str, *, genre: str):
        """Displays a random anime or manga of the specified genre."""
        async with ctx.channel.typing():
            if media.lower() == 'anime':
                embed = await self.anilist_random(genre, 'anime', ['TV', 'MOVIE'])
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title=f'An anime with the genre `{genre}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            elif media.lower() == 'manga':
                embed = await self.anilist_random(genre, 'manga', ['MANGA'])
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title=f'A manga with the genre `{genre}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                ctx.command.reset_cooldown(ctx)
                raise discord.ext.commands.BadArgument
