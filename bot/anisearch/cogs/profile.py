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
import re
from typing import Optional, Union, List
from urllib.parse import urljoin, quote

import discord
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, KITSU_LOGO, MYANIMELIST_LOGO, \
    ANILIST_LOGO, KITSU_BASE_URL
from anisearch.utils.http import get
from anisearch.utils.menus import EmbedListMenu

log = logging.getLogger(__name__)


class Profile(commands.Cog, name='Profile'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    async def set_profile(self, ctx: Context, site: str, username: str):

        data = None

        try:
            if site == 'anilist':
                data = await self.bot.anilist.user(name=username, page=1, perPage=1)
            if site == 'myanimelist':
                data = await self.bot.jikan.user(username=username)
            if site == 'kitsu':
                params = {
                    'filter[name]': username,
                    'include': 'stats'
                }
                data = await get(url=urljoin(KITSU_BASE_URL, 'users'), session=self.bot.session,
                                 res_method='json', params=params)
                if not data.get('data'):
                    data = None

        except Exception as e:
            log.exception(e)

            site = site.replace("anilist", "AniList").replace(
                "myanimelist", "MyAnimeList").replace("kitsu", "Kitsu")
            embed = discord.Embed(
                color=ERROR_EMBED_COLOR,
                title=f'An error occurred while setting the {site} profile `{username}`.')

            return await ctx.channel.send(embed=embed)

        if data is not None:
            if site == 'anilist':
                self.bot.db.insert_profile(
                    'anilist', data.get('name'), ctx.author.id)

                embed = discord.Embed(
                    title=f'Added AniList Profile `{data.get("name")}`', color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)

                if data.get('avatar')['large']:
                    embed.set_thumbnail(url=data.get('avatar')['large'])

                embed.add_field(
                    name='Anime Stats', inline=True,
                    value=f'Anime Count: {data.get("statistics")["anime"]["count"]}\n'
                          f'Mean Score: {data.get("statistics")["anime"]["meanScore"]}\n'
                          f'Days Watched: {round(data.get("statistics")["anime"]["minutesWatched"] / 60 / 24, 2)}')
                embed.add_field(
                    name='Manga Stats', inline=True,
                    value=f'Manga Count: {data.get("statistics")["manga"]["count"]}\n'
                          f'Mean Score: {data.get("statistics")["manga"]["meanScore"]}\n'
                          f'Chapters Read: {data.get("statistics")["manga"]["chaptersRead"]}')

                embed.set_footer(text=f'Provided by https://anilist.co/')

                await ctx.channel.send(embed=embed)

            if site == 'myanimelist':
                self.bot.db.insert_profile(
                    'myanimelist', data.get('username'), ctx.author.id)

                embed = discord.Embed(title=f'Added MyAnimeList Profile `{data.get("username")}`',
                                      color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='MyAnimeList Profile',
                                 icon_url=MYANIMELIST_LOGO)

                if data.get('image_url'):
                    embed.set_thumbnail(url=data.get('image_url'))

                embed.add_field(
                    name='Anime Stats', inline=True,
                    value=f'Days Watched: {data.get("anime_stats")["days_watched"]}\n'
                          f'Mean Score: {data.get("anime_stats")["mean_score"]}\n'
                          f'Total Entries: {data.get("anime_stats")["total_entries"]}')
                embed.add_field(
                    name='Manga Stats', inline=True,
                    value=f'Days Read: {data.get("manga_stats")["days_read"]}\n'
                          f'Mean Score: {data.get("manga_stats")["mean_score"]}\n'
                          f'Total Entries: {data.get("manga_stats")["total_entries"]}')

                embed.set_footer(text=f'Provided by https://myanimelist.net/')

                await ctx.channel.send(embed=embed)

            if site == 'kitsu':
                user = data.get('data')[0]

                self.bot.db.insert_profile('kitsu', user.get(
                    'attributes')['name'], ctx.author.id)

                embed = discord.Embed(title=f'Added Kitsu Profile `{user.get("attributes")["name"]}`',
                                      color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='Kitsu Profile', icon_url=KITSU_LOGO)

                if user.get('attributes')['avatar']:
                    embed.set_thumbnail(url=user.get('attributes')[
                                        'avatar']['original'])

                anime_completed = 'N/A'
                anime_episodes_watched = 'N/A'
                anime_total_entries = 'N/A'
                manga_total_entries = 'N/A'
                manga_chapters = 'N/A'
                manga_completed = 'N/A'
                stats = 0
                for x in data['included']:
                    if stats == 2:
                        break
                    try:
                        if x['attributes']:
                            if x['attributes']['kind'] == 'anime-amount-consumed':
                                if x['attributes']['statsData']:
                                    try:
                                        anime_stats = x['attributes']['statsData']
                                        anime_completed = anime_stats['completed']
                                        anime_total_entries = anime_stats['media']
                                        anime_episodes_watched = anime_stats['units']
                                        stats += 1
                                    except Exception as e:
                                        log.exception(e)
                            if x['attributes']['kind'] == 'manga-amount-consumed':
                                if x['attributes']['statsData']:
                                    try:
                                        manga_stats = x['attributes']['statsData']
                                        manga_chapters = manga_stats['units']
                                        manga_completed = manga_stats['completed']
                                        manga_total_entries = manga_stats['media']
                                        stats += 1
                                    except Exception as e:
                                        log.exception(e)
                    except KeyError:
                        pass
                    except Exception as e:
                        log.exception(e)
                embed.add_field(name='Anime Stats', value=f'Episodes: {anime_episodes_watched}\n'
                                                          f'Completed: {anime_completed}\n'
                                                          f'Total Entries: {anime_total_entries}\n',
                                inline=True)
                embed.add_field(name='Manga Stats', value=f'Chapters: {manga_chapters}\n'
                                                          f'Completed: {manga_completed}\n'
                                                          f'Total Entries: {manga_total_entries}\n',
                                inline=True)

                embed.set_footer(text=f'Provided by https://kitsu.io/')

                await ctx.channel.send(embed=embed)

        else:
            site = site.replace("anilist", "AniList").replace(
                "myanimelist", "MyAnimeList").replace("kitsu", "Kitsu")
            embed = discord.Embed(title=f'The {site} profile `{username}` could not be found.',
                                  color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    async def get_anilist_profile(self, username: str) -> Union[List[discord.Embed], None]:

        embeds = []

        try:
            data = await self.bot.anilist.user(name=username, page=1, perPage=1)

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching the AniList profile `{username}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:

            try:
                embed = discord.Embed(title=data.get('name'), url=data.get(
                    'siteUrl'), color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)

                if data.get('avatar')['large']:
                    embed.set_thumbnail(url=data.get('avatar')['large'])
                if data.get('bannerImage'):
                    embed.set_image(url=data.get('bannerImage'))
                if data.get('about'):
                    embed.add_field(name='About',
                                    value=data.get('about')[0:500] + '...' if len(data.get('about')) >= 500
                                    else data.get('about'), inline=False)

                embed.add_field(
                    name='Anime Stats', inline=True,
                    value=f'Anime Count: {data.get("statistics")["anime"]["count"]}\n'
                          f'Mean Score: {data.get("statistics")["anime"]["meanScore"]}\n'
                          f'Days Watched: {round(data.get("statistics")["anime"]["minutesWatched"] / 60 / 24, 2)}\n'
                          f'Episodes: {data.get("statistics")["anime"]["episodesWatched"]}')

                embed.add_field(
                    name='Manga Stats', inline=True,
                    value=f'Manga Count: {data.get("statistics")["manga"]["count"]}\n'
                          f'Mean Score: {data.get("statistics")["manga"]["meanScore"]}\n'
                          f'Chapters Read: {data.get("statistics")["manga"]["chaptersRead"]}\n'
                          f'Volumes Read: {data.get("statistics")["manga"]["volumesRead"]}')

                embed.add_field(name='Anime List', value=f'https://anilist.co/user/{data.get("name")}/animelist',
                                inline=False)

                embed.add_field(name='Manga List', value=f'https://anilist.co/user/{data.get("name")}/mangalist',
                                inline=False)

                embed.set_footer(
                    text=f'Provided by https://anilist.co/ • Page 1/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the AniList profile.')
                embed.set_footer(
                    text=f'Provided by https://anilist.co/ • Page 1/2')
                embeds.append(embed)

            try:
                embed = discord.Embed(title=data.get('name'), url=data.get(
                    'siteUrl'), color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)

                if data.get('avatar')['large']:
                    embed.set_thumbnail(url=data.get('avatar')['large'])

                if data.get('favourites')['anime']['nodes']:
                    fav_anime = []
                    for anime in data.get('favourites')['anime']['nodes']:
                        fav_anime.append(
                            f"[{anime.get('title')['romaji']}]({anime.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_anime):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_anime = fav_anime[0:i]
                            fav_anime[i-1] = fav_anime[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Anime',
                                    value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime',
                                    value='N/A', inline=False)

                if data.get('favourites')['manga']['nodes']:
                    fav_manga = []
                    for manga in data.get('favourites')['manga']['nodes']:
                        fav_manga.append(
                            f"[{manga.get('title')['romaji']}]({manga.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_manga):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_manga = fav_manga[0:i]
                            fav_manga[i-1] = fav_manga[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Manga',
                                    value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga',
                                    value='N/A', inline=False)

                if data.get('favourites')['characters']['nodes']:
                    fav_characters = []
                    for character in data.get('favourites')['characters']['nodes']:
                        fav_characters.append(
                            f"[{character.get('name')['full']}]({character.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_characters):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_characters = fav_characters[0:i]
                            fav_characters[i-1] = fav_characters[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Characters', value=' | '.join(
                        fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters',
                                    value='N/A', inline=False)

                if data.get('favourites')['staff']['nodes']:
                    fav_staff = []
                    for staff in data.get('favourites')['staff']['nodes']:
                        fav_staff.append(
                            f"[{staff.get('name')['full']}]({staff.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_staff):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_staff = fav_staff[0:i]
                            fav_staff[i-1] = fav_staff[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Staff',
                                    value=' | '.join(fav_staff), inline=False)
                else:
                    embed.add_field(name='Favorite Staff',
                                    value='N/A', inline=False)

                if data.get('favourites')['studios']['nodes']:
                    fav_studio = []
                    for studio in data.get('favourites')['studios']['nodes']:
                        fav_studio.append(
                            f"[{studio.get('name')}]({studio.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_studio):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_studio = fav_studio[0:i]
                            fav_studio[i-1] = fav_studio[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Studios',
                                    value=' | '.join(fav_studio), inline=False)
                else:
                    embed.add_field(name='Favorite Studios',
                                    value='N/A', inline=False)

                embed.set_footer(
                    text=f'Provided by https://anilist.co/ • Page 2/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the AniList profile.')
                embed.set_footer(
                    text=f'Provided by https://anilist.co/ • Page 2/2')
                embeds.append(embed)

            return embeds

        return None

    async def get_myanimelist_profile(self, username: str) -> Union[List[discord.Embed], None]:

        embeds = []

        try:
            data = await self.bot.jikan.user(username=username)

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching the MyAnimeList profile `{username}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:

            try:
                description = []
                if data.get('last_online'):
                    last_online = data.get('last_online').__str__().replace('-', '/') \
                        .replace('T', ' ').replace('+', ' +').replace('+00:00', 'UTC')
                    description.append(f'**Last Online:** {last_online}')
                if data.get('gender'):
                    description.append(f'**Gender:** {data.get("gender")}')
                if data.get('birthday'):
                    birthday = data.get('birthday').__str__().replace(
                        'T00:00:00+00:00', ' ').replace('-', '/')
                    description.append(f'**Birthday:** {birthday}')
                if data.get('location'):
                    description.append(f'**Location:** {data.get("location")}')
                if data.get('joined'):
                    joined = data.get('joined').__str__().replace(
                        'T00:00:00+00:00', ' ').replace('-', '/')
                    description.append(f'**Joined:** {joined}')

                embed = discord.Embed(title=data.get('username'), url=data.get('url'), color=DEFAULT_EMBED_COLOR,
                                      description='\n'.join(description))

                embed.set_author(name='MyAnimeList Profile',
                                 icon_url=MYANIMELIST_LOGO)

                if data.get('image_url'):
                    embed.set_thumbnail(url=data.get('image_url'))

                if data.get('about'):
                    embed.add_field(name='About',
                                    value=data.get('about')[0:500] + '...' if len(data.get('about')) >= 500
                                    else data.get('about'), inline=False)

                embed.add_field(
                    name='Anime Stats', inline=True,
                    value=f'Days Watched: {data.get("anime_stats")["days_watched"]}\n'
                          f'Mean Score: {data.get("anime_stats")["mean_score"]}\n'
                          f'Watching: {data.get("anime_stats")["watching"]}\n'
                          f'Completed: {data.get("anime_stats")["completed"]}\n'
                          f'On-Hold: {data.get("anime_stats")["on_hold"]}\n'
                          f'Dropped: {data.get("anime_stats")["dropped"]}\n'
                          f'Plan to Watch: {data.get("anime_stats")["plan_to_watch"]}\n'
                          f'Total Entries: {data.get("anime_stats")["total_entries"]}\n'
                          f'Rewatched: {data.get("anime_stats")["rewatched"]}\n'
                          f'Episodes: {data.get("anime_stats")["episodes_watched"]}')

                embed.add_field(
                    name='Manga Stats', inline=True,
                    value=f'Days Read: {data.get("manga_stats")["days_read"]}\n'
                          f'Mean Score: {data.get("manga_stats")["mean_score"]}\n'
                          f'Reading: {data.get("manga_stats")["reading"]}\n'
                          f'Completed: {data.get("manga_stats")["completed"]}\n'
                          f'On-Hold: {data.get("manga_stats")["on_hold"]}\n'
                          f'Dropped: {data.get("manga_stats")["dropped"]}\n'
                          f'Plan to Read: {data.get("manga_stats")["plan_to_read"]}\n'
                          f'Reread: {data.get("manga_stats")["reread"]}\n'
                          f'Total Entries: {data.get("manga_stats")["total_entries"]}\n'
                          f'Chapters Read: {data.get("manga_stats")["chapters_read"]}\n'
                          f'Volumes Read: {data.get("manga_stats")["volumes_read"]}')

                embed.add_field(name='Anime List', inline=False,
                                value=f'https://myanimelist.net/animelist/{data.get("username")}')

                embed.add_field(name='Manga List', inline=False,
                                value=f'https://myanimelist.net/mangalist/{data.get("username")}')

                embed.set_footer(
                    text=f'Provided by https://myanimelist.net/ • Page 1/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the MyAnimeList profile.')
                embed.set_footer(
                    text=f'Provided by https://myanimelist.net/ • Page 1/2')
                embeds.append(embed)

            try:
                embed = discord.Embed(title=data.get('username'),
                                      url=data.get('url'), color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='MyAnimeList Profile',
                                 icon_url=MYANIMELIST_LOGO)

                if data.get('image_url'):
                    embed.set_thumbnail(url=data.get('image_url'))

                if data.get('favorites')['anime']:
                    fav_anime = []
                    for anime in data.get('favorites')['anime']:
                        fav_anime.append(
                            f"[{anime.get('name')}]({anime.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_anime):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_anime = fav_anime[0:i]
                            fav_anime[i-1] = fav_anime[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Anime',
                                    value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime',
                                    value='N/A', inline=False)

                if data.get('favorites')['manga']:
                    fav_manga = []
                    for manga in data.get('favorites')['manga']:
                        fav_manga.append(
                            f"[{manga.get('name')}]({manga.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_manga):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_manga = fav_manga[0:i]
                            fav_manga[i-1] = fav_manga[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Manga',
                                    value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga',
                                    value='N/A', inline=False)

                if data.get('favorites')['characters']:
                    fav_characters = []
                    for character in data.get('favorites')['characters']:
                        fav_characters.append(
                            f"[{character.get('name')}]({character.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_characters):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_characters = fav_characters[0:i]
                            fav_characters[i-1] = fav_characters[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Characters', value=' | '.join(
                        fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters',
                                    value='N/A', inline=False)

                if data.get('favorites')['people']:
                    fav_people = []
                    for people in data.get('favorites')['people']:
                        fav_people.append(
                            f"[{people.get('name')}]({people.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_people):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_people = fav_people[0:i]
                            fav_people[i-1] = fav_people[i-1] + '...'
                            break
                    embed.add_field(name='Favorite People',
                                    value=' | '.join(fav_people), inline=False)
                else:
                    embed.add_field(name='Favorite People',
                                    value='N/A', inline=False)

                embed.set_footer(
                    text=f'Provided by https://myanimelist.net/ • Page 2/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the MyAnimeList profile.')
                embed.set_footer(
                    text=f'Provided by https://myanimelist.net/ • Page 2/2')
                embeds.append(embed)

            return embeds

        return None

    async def get_kitsu_profile(self, username: str) -> Union[List[discord.Embed], None]:

        embeds = []

        try:
            params = {
                'filter[name]': username,
                'include': 'stats,favorites.item'
            }
            data = await get(url=urljoin(KITSU_BASE_URL, 'users'), session=self.bot.session,
                             res_method='json', params=params)
            if not data.get('data'):
                data = None

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching the Kitsu profile `{username}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:

            try:
                description = []
                if data.get('data')[0].get('attributes').get('gender'):
                    gender = data.get('data')[0].get('attributes').get('gender') \
                        .replace('male', 'Male').replace('feMale', 'Female')
                    description.append(f'**Gender:** {gender}')
                if data.get('data')[0].get('attributes').get('birthday'):
                    birthday = data.get('data')[0].get(
                        'attributes').get('birthday')
                    description.append(f'**Birthday:** {birthday}')
                if data.get('data')[0].get('attributes').get('location'):
                    location = data.get('data')[0].get(
                        'attributes').get('location')
                    description.append(f'**Location:** {location}')
                if data.get('data')[0].get('attributes').get('createdAt'):
                    createdAt = data.get('data')[0].get(
                        'attributes').get('createdAt').split('T')
                    createdAt = createdAt[0]
                    description.append(f'**Created at:** {createdAt}')
                if data.get('data')[0].get('attributes').get('updatedAt'):
                    updatedAt = data.get('data')[0].get(
                        'attributes').get('updatedAt').split('T')
                    updatedAt = updatedAt[0]
                    description.append(f'**Updated at:** {updatedAt}')

                embed = discord.Embed(title=data.get('data')[0]['attributes']['name'],
                                      url=f'https://kitsu.io/users/{data.get("data")[0].get("id")}',
                                      color=DEFAULT_EMBED_COLOR, description='\n'.join(description))

                embed.set_author(name='Kitsu Profile', icon_url=KITSU_LOGO)

                if data.get('data')[0].get('attributes').get('avatar'):
                    embed.set_thumbnail(url=data.get(
                        'data')[0]['attributes']['avatar']['original'])

                if data.get('data')[0].get('attributes').get('coverImage'):
                    embed.set_image(url=data.get('data')[
                                    0]['attributes']['coverImage']['original'])

                anime_days_watched = 'N/A'
                anime_completed = 'N/A'
                anime_episodes_watched = 'N/A'
                anime_total_entries = 'N/A'
                manga_total_entries = 'N/A'
                manga_chapters = 'N/A'
                manga_completed = 'N/A'
                stats = 0
                for x in data['included']:
                    if stats == 2:
                        break
                    try:
                        if x['attributes']:
                            if x['attributes']['kind'] == 'anime-amount-consumed':
                                if x['attributes']['statsData']:
                                    try:
                                        anime_stats = x['attributes']['statsData']
                                        anime_days_watched = \
                                            str(datetime.timedelta(
                                                seconds=anime_stats['time'])).split(',')
                                        anime_days_watched = anime_days_watched[0]
                                        anime_completed = anime_stats['completed']
                                        anime_total_entries = anime_stats['media']
                                        anime_episodes_watched = anime_stats['units']
                                        stats += 1
                                    except Exception as e:
                                        log.exception(e)
                            if x['attributes']['kind'] == 'manga-amount-consumed':
                                if x['attributes']['statsData']:
                                    try:
                                        manga_stats = x['attributes']['statsData']
                                        manga_chapters = manga_stats['units']
                                        manga_completed = manga_stats['completed']
                                        manga_total_entries = manga_stats['media']
                                        stats += 1
                                    except Exception as e:
                                        log.exception(e)
                    except KeyError:
                        pass
                    except Exception as e:
                        log.exception(e)

                embed.add_field(name='Anime Stats', value=f'Episodes: {anime_episodes_watched}\n'
                                                          f'Completed: {anime_completed}\n'
                                                          f'Total Entries: {anime_total_entries}\n'
                                                          f'Days Watched: {anime_days_watched}',
                                inline=True)
                embed.add_field(name='Manga Stats', value=f'Chapters: {manga_chapters}\n'
                                                          f'Completed: {manga_completed}\n'
                                                          f'Total Entries: {manga_total_entries}',
                                inline=True)

                embed.add_field(name='Anime List', inline=False,
                                value=f'https://kitsu.io/users/{data.get("data")[0]["attributes"]["name"]}'
                                      f'/library?media=anime')

                embed.add_field(name='Manga List', inline=False,
                                value=f'https://kitsu.io/users/{data.get("data")[0]["attributes"]["name"]}'
                                      f'/library?media=manga')

                embed.set_footer(
                    text=f'Provided by https://kitsu.io/ • Page 1/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the Kitsu profile.')
                embed.set_footer(
                    text=f'Provided by https://kitsu.io/ • Page 1/2')
                embeds.append(embed)

            try:
                embed = discord.Embed(title=data.get('data')[0]['attributes']['name'],
                                      url=f'https://kitsu.io/users/{data.get("data")[0].get("id")}',
                                      color=DEFAULT_EMBED_COLOR)

                embed.set_author(name='Kitsu Profile', icon_url=KITSU_LOGO)

                fav_anime = []
                fav_manga = []
                fav_characters = []
                for i in data.get('included'):
                    if i.get('type') == 'anime':
                        fav_anime.append(f'[{i.get("attributes").get("titles").get("en_jp")}]'
                                         f'(https://kitsu.io/anime/{i.get("attributes").get("slug")})')
                    if i.get('type') == 'manga':
                        fav_manga.append(f'[{i.get("attributes").get("titles").get("en_jp")}]'
                                         f'(https://kitsu.io/manga/{i.get("attributes").get("slug")})')
                    if i.get('type') == 'characters':
                        fav_characters.append(f'[{i.get("attributes").get("names").get("en")}]'
                                              f'(https://myanimelist.net/character/{i.get("attributes").get("malId")})')

                if len(fav_anime) > 0:
                    total = 0
                    for i, fav in enumerate(fav_anime):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_anime = fav_anime[0:i]
                            fav_anime[i-1] = fav_anime[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Anime',
                                    value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime',
                                    value='N/A', inline=False)

                if len(fav_manga) > 0:
                    total = 0
                    for i, fav in enumerate(fav_manga):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_manga = fav_manga[0:i]
                            fav_manga[i-1] = fav_manga[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Manga',
                                    value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga',
                                    value='N/A', inline=False)

                if len(fav_characters) > 0:
                    total = 0
                    for i, fav in enumerate(fav_characters):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_characters = fav_characters[0:i]
                            fav_characters[i-1] = fav_characters[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Characters', value=' | '.join(
                        fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters',
                                    value='N/A', inline=False)

                embed.set_footer(
                    text=f'Provided by https://kitsu.io/ • Page 2/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the Kitsu profile.')
                embed.set_footer(
                    text=f'Provided by https://kitsu.io/ • Page 2/2')
                embeds.append(embed)

            return embeds

        return None

    @commands.command(name='anilist', aliases=['al'], usage='anilist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anilist(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given AniList profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            if username is None:
                username = self.bot.db.select_profile('anilist', ctx.author.id)
            elif username.startswith('<@') and username.endswith('>'):
                id_ = re.match(
                    r'^<@[!|&]?(?P<id>\d{17,18})>', username).group('id')
                username = self.bot.db.select_profile('anilist', int(id_))
            else:
                username = username
            if username:
                embeds = await self.get_anilist_profile(username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(
                        embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title=f'The AniList profile `{username}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title='No AniList profile added.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='myanimelist', aliases=['mal'], usage='myanimelist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def myanimelist(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given MyAnimeList profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            if username is None:
                username = self.bot.db.select_profile(
                    'myanimelist', ctx.author.id)
            elif username.startswith('<@') and username.endswith('>'):
                id_ = re.match(
                    r'^<@[!|&]?(?P<id>\d{17,18})>', username).group('id')
                username = self.bot.db.select_profile('myanimelist', int(id_))
            else:
                username = username
            if username:
                embeds = await self.get_myanimelist_profile(username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(
                        embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title=f'The MyAnimeList profile `{username}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title='No MyAnimeList profile added.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='kitsu', usage='kitsu [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kitsu(self, ctx: Context, username: Optional[str] = None):
        """Displays information about the given Kitsu profile such as anime stats, manga stats and favorites!"""
        async with ctx.channel.typing():
            if username is None:
                username = self.bot.db.select_profile('kitsu', ctx.author.id)
            elif username.startswith('<@') and username.endswith('>'):
                id_ = re.match(
                    r'^<@[!|&]?(?P<id>\d{17,18})>', username).group('id')
                username = self.bot.db.select_profile('kitsu', int(id_))
            else:
                username = username
            if username:
                embeds = await self.get_kitsu_profile(username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(
                        embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title=f'The Kitsu profile `{username}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title='No Kitsu profile added.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='addprofile', aliases=['addp'], usage='addprofile <al|mal|kitsu> <username>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def addprofile(self, ctx: Context, site: str, username: str):
        """Adds an AniList, MyAnimeList or Kitsu profile."""
        async with ctx.channel.typing():
            if site.lower() == 'anilist' or site.lower() == 'al':
                await self.set_profile(ctx, 'anilist', username)
            elif site.lower() == 'myanimelist' or site.lower() == 'mal':
                await self.set_profile(ctx, 'myanimelist', username)
            elif site.lower() == 'kitsu':
                await self.set_profile(ctx, 'kitsu', username)
            else:
                ctx.command.reset_cooldown(ctx)
                raise discord.ext.commands.BadArgument

    @commands.command(name='profiles', usage='profiles [@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profiles(self, ctx: Context, user: Optional[str] = None):
        """Displays the added profiles of you, or the specified user."""
        async with ctx.channel.typing():
            if user:
                if user.startswith('<@&') and user.endswith('>'):
                    ctx.command.reset_cooldown(ctx)
                    raise discord.ext.commands.BadArgument
                if user.startswith('<@') and user.endswith('>'):
                    id_ = re.match(
                        r'^<@(!)?(?P<id>\d{17,18})>', user).group('id')
                else:
                    ctx.command.reset_cooldown(ctx)
                    raise discord.ext.commands.BadArgument
            else:
                id_ = ctx.author.id
            anilist = self.bot.db.select_profile('anilist', id_)
            myanimelist = self.bot.db.select_profile('myanimelist', id_)
            kitsu = self.bot.db.select_profile('kitsu', id_)
            user = await self.bot.fetch_user(id_)
            embed = discord.Embed(title=user, color=DEFAULT_EMBED_COLOR)
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(
                name='AniList', value=anilist if anilist else '*Not added*', inline=False)
            embed.add_field(
                name='MyAnimeList', value=myanimelist if myanimelist else '*Not added*', inline=False)
            embed.add_field(
                name='Kitsu', value=kitsu if kitsu else '*Not added*', inline=False)
            await ctx.channel.send(embed=embed)

    @commands.command(name='removeprofile', aliases=['rmp'], usage='removeprofile <al|mal|kitsu|all>',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def removeprofile(self, ctx: Context, site: str,):
        """Removes the added AniList, MyAnimeList or Kitsu profile."""
        async with ctx.channel.typing():
            if site.lower() == 'anilist' or site.lower() == 'al':
                anilist = self.bot.db.select_profile('anilist', ctx.author.id)
                if anilist is None:
                    embed = discord.Embed(title='No AniList profile added.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    self.bot.db.insert_profile('anilist', None, ctx.author.id)
                    embed = discord.Embed(title='Removed the added AniList profile.', color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            elif site.lower() == 'myanimelist' or site.lower() == 'mal':
                myanimelist = self.bot.db.select_profile('myanimelist', ctx.author.id)
                if myanimelist is None:
                    embed = discord.Embed(title='No MyAnimeList profile added.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    self.bot.db.insert_profile('myanimelist', None, ctx.author.id)
                    embed = discord.Embed(title='Removed the added MyAnimeList profile.', color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            elif site.lower() == 'kitsu':
                kitsu = self.bot.db.select_profile('kitsu', ctx.author.id)
                if kitsu is None:
                    embed = discord.Embed(title='No Kitsu profile added.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    self.bot.db.insert_profile('kitsu', None, ctx.author.id)
                    embed = discord.Embed(title='Removed the added Kitsu profile.', color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            elif site.lower() == 'all':
                if not self.bot.db.check_user(ctx.author.id):
                    embed = discord.Embed(title=f'The user {ctx.author} does not exist in the database.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                else:
                    self.bot.db.delete_user(ctx.author.id)
                    embed = discord.Embed(title=f'Removed the user {ctx.author} from the database.',
                                          color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                ctx.command.reset_cooldown(ctx)
                raise discord.ext.commands.BadArgument


def setup(bot: AniSearchBot):
    bot.add_cog(Profile(bot))
    log.info('Profile cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Profile cog unloaded')
