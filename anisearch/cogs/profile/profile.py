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
from typing import Optional, Union, List

import discord
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Profile(commands.Cog, name='Profile'):
    """
    Profile cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Profile` cog.
        """
        self.bot = bot

    async def set_profile(self, ctx: Context, site: str, username: str):
        """
        Checks if the profile exists on the specified site and inserts it into the database if it does.

        Args:
            ctx (Context): The context in which the command was invoked under.
            site (str): The anime tracking site (`anilist`, `myanimelist`, `kitsu`).
            username (str): The profile name.
        """

        data = None

        try:
            if site == 'anilist':
                data = await self.bot.anilist.user(name=username, page=1, perPage=1)
            if site == 'myanimelist':
                data = await self.bot.myanimelist.user(username=username)
            if site == 'kitsu':
                data = await self.bot.kitsu.user(username=username)

        except Exception as e:
            log.exception(e)

            site = site.replace("anilist", "AniList").replace("myanimelist", "MyAnimeList").replace("kitsu", "Kitsu")
            embed = discord.Embed(
                color=ERROR_EMBED_COLOR,
                title=f'An error occurred while setting the {site} profile `{username}`.')

            return await ctx.channel.send(embed=embed)

        if data is not None:
            if site == 'anilist':
                self.bot.db.insert_profile('anilist', data.get('name'), ctx.author.id)

                embed = discord.Embed(title=f'Set AniList Profile `{data.get("name")}`', color=DEFAULT_EMBED_COLOR)

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
                self.bot.db.insert_profile('myanimelist', data.get('username'), ctx.author.id)

                embed = discord.Embed(title=f'Set MyAnimeList Profile `{data.get("username")}`',
                                      color=DEFAULT_EMBED_COLOR)

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

                self.bot.db.insert_profile('kitsu', user.get('attributes')['name'], ctx.author.id)

                embed = discord.Embed(title=f'Set Kitsu Profile `{user.get("attributes")["name"]}`',
                                      color=DEFAULT_EMBED_COLOR)

                if user.get('attributes')['avatar']:
                    embed.set_thumbnail(url=user.get('attributes')['avatar']['original'])

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
            site = site.replace("anilist", "AniList").replace("myanimelist", "MyAnimeList").replace("kitsu", "Kitsu")
            embed = discord.Embed(title=f'The {site} profile `{username}` could not be found.',
                                  color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    async def show_profiles(self, ctx: Context, id_: int):
        """
        Selects the set profiles of a user from the database and sends an embed with the profiles in the channel.

        Args:
            ctx (Context): The context in which the command was invoked under.
            id_ (int): The ID of the discord user.
        """
        anilist = self.bot.db.select_profile('anilist', id_)
        myanimelist = self.bot.db.select_profile('myanimelist', id_)
        kitsu = self.bot.db.select_profile('kitsu', id_)
        user = await self.bot.fetch_user(id_)
        embed = discord.Embed(title=user.name, color=DEFAULT_EMBED_COLOR)
        embed.add_field(name='AniList', value=anilist if anilist else '*Not Set*', inline=False)
        embed.add_field(name='MyAnimeList', value=myanimelist if myanimelist else '*Not Set*', inline=False)
        embed.add_field(name='Kitsu', value=kitsu if kitsu else '*Not Set*', inline=False)
        await ctx.channel.send(embed=embed)

    async def get_anilist_profile(self, username: str) -> Union[List[discord.Embed], None]:
        """
        Returns a list of Discord embeds with the retrieved AniList data about the searched profile.

        Args:
            username (str): The profile name.

        Returns:
            list (Embed): A list of discord embeds.
            None: If no profile was found.
        """
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
                embed = discord.Embed(title=f'{data.get("name")} - AniList',
                                      url=data.get('siteUrl'), color=DEFAULT_EMBED_COLOR)

                if data.get('avatar')['large']:
                    embed.set_thumbnail(url=data.get('avatar')['large'])
                if data.get('bannerImage'):
                    embed.set_image(url=data.get('bannerImage'))
                if data.get('about'):
                    embed.add_field(name='About',
                                    value=data.get('about')[0:500] + '...' if len(data.get('about')) >= 500
                                    else data.get('about'), inline=False)
                else:
                    embed.add_field(name='About', value='N/A', inline=False)

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

                embed.add_field(name='Anime List', value='https://anilist.co/user/%s/animelist' % data.get('name'),
                                inline=False)

                embed.add_field(name='Manga List', value='https://anilist.co/user/%s/mangalist' % data.get('name'),
                                inline=False)

                embed.set_footer(text=f'Provided by https://anilist.co/ • Page 1/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the AniList profile.')
                embed.set_footer(text=f'Provided by https://anilist.co/ • Page 1/2')
                embeds.append(embed)

            try:
                embed = discord.Embed(title=f'{data.get("name")} - AniList',
                                      url=data.get('siteUrl'), color=DEFAULT_EMBED_COLOR)

                if data.get('avatar')['large']:
                    embed.set_thumbnail(url=data.get('avatar')['large'])

                if data.get('favourites')['anime']['nodes']:
                    fav_anime = []
                    for anime in data.get('favourites')['anime']['nodes']:
                        fav_anime.append(f"[{anime.get('title')['romaji']}]({anime.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_anime):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_anime = fav_anime[0:i]
                            fav_anime[i-1] = fav_anime[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Anime', value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime', value='N/A', inline=False)

                if data.get('favourites')['manga']['nodes']:
                    fav_manga = []
                    for manga in data.get('favourites')['manga']['nodes']:
                        fav_manga.append(f"[{manga.get('title')['romaji']}]({manga.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_manga):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_manga = fav_manga[0:i]
                            fav_manga[i-1] = fav_manga[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Manga', value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga', value='N/A', inline=False)

                if data.get('favourites')['characters']['nodes']:
                    fav_characters = []
                    for character in data.get('favourites')['characters']['nodes']:
                        fav_characters.append(f"[{character.get('name')['full']}]({character.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_characters):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_characters = fav_characters[0:i]
                            fav_characters[i-1] = fav_characters[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Characters', value=' | '.join(fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters', value='N/A', inline=False)

                if data.get('favourites')['staff']['nodes']:
                    fav_staff = []
                    for staff in data.get('favourites')['staff']['nodes']:
                        fav_staff.append(f"[{staff.get('name')['full']}]({staff.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_staff):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_staff = fav_staff[0:i]
                            fav_staff[i-1] = fav_staff[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Staff', value=' | '.join(fav_staff), inline=False)
                else:
                    embed.add_field(name='Favorite Staff', value='N/A', inline=False)

                if data.get('favourites')['studios']['nodes']:
                    fav_studio = []
                    for studio in data.get('favourites')['studios']['nodes']:
                        fav_studio.append(f"[{studio.get('name')}]({studio.get('siteUrl')})")
                    total = 0
                    for i, fav in enumerate(fav_studio):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_studio = fav_studio[0:i]
                            fav_studio[i-1] = fav_studio[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Studios', value=' | '.join(fav_studio), inline=False)
                else:
                    embed.add_field(name='Favorite Studios', value='N/A', inline=False)

                embed.set_footer(text=f'Provided by https://anilist.co/ • Page 2/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the AniList profile.')
                embed.set_footer(text=f'Provided by https://anilist.co/ • Page 2/2')
                embeds.append(embed)

            return embeds

        return None

    async def get_myanimelist_profile(self, username: str) -> Union[List[discord.Embed], None]:
        """
        Returns a list of Discord embeds with the retrieved MyAnimeList data about the searched profile.

        Args:
            username (str): The profile name.

        Returns:
            list (Embed): A list of discord embeds.
            None: If no profile was found.
        """
        embeds = []

        try:
            data = await self.bot.myanimelist.user(username=username)

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching the MyAnimeList profile `{username}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:

            try:
                last_online = None
                if data.get('last_online'):
                    last_online = data.get('last_online').__str__().replace('-', '/') \
                        .replace('T', ' ').replace('+', ' +').replace('+00:00', 'UTC')
                joined = None
                if data.get('joined'):
                    joined = data.get('joined').__str__().replace('T00:00:00+00:00', ' ').replace('-', '/')
                birthday = None
                if data.get('birthday'):
                    birthday = data.get('birthday').__str__().replace('T00:00:00+00:00', ' ').replace('-', '/')

                embed = discord.Embed(
                    title=f'{data.get("username")} - MyAnimeList',
                    url=data.get('url'), color=DEFAULT_EMBED_COLOR,
                    description=
                    f'**Last Online:** {last_online if data.get("last_online") else "N/A"}\n'
                    f'**Gender:** {data.get("gender") if data.get("gender") else "N/A"}\n'
                    f'**Birthday:** {birthday if data.get("birthday") else "N/A"}\n'
                    f'**Location:** {data.get("location") if data.get("location") else "N/A"}\n'
                    f'**Joined:** {joined if data.get("joined") else "N/A"}\n'
                )

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
                                value='https://myanimelist.net/animelist/{}'.format(data.get('username')))

                embed.add_field(name='Manga List', inline=False,
                                value='https://myanimelist.net/mangalist/{}'.format(data.get('username')))

                embed.set_footer(text=f'Provided by https://myanimelist.net/ • Page 1/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the MyAnimeList profile.')
                embed.set_footer(text=f'Provided by https://myanimelist.net/ • Page 1/2')
                embeds.append(embed)

            try:
                embed = discord.Embed(title=f'{data.get("username")} - MyAnimeList',
                                      url=data.get('url'), color=DEFAULT_EMBED_COLOR)

                if data.get('image_url'):
                    embed.set_thumbnail(url=data.get('image_url'))

                if data.get('favorites')['anime']:
                    fav_anime = []
                    for anime in data.get('favorites')['anime']:
                        fav_anime.append(f"[{anime.get('name')}]({anime.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_anime):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_anime = fav_anime[0:i]
                            fav_anime[i-1] = fav_anime[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Anime', value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime', value='N/A', inline=False)

                if data.get('favorites')['manga']:
                    fav_manga = []
                    for manga in data.get('favorites')['manga']:
                        fav_manga.append(f"[{manga.get('name')}]({manga.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_manga):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_manga = fav_manga[0:i]
                            fav_manga[i-1] = fav_manga[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Manga', value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga', value='N/A', inline=False)

                if data.get('favorites')['characters']:
                    fav_characters = []
                    for character in data.get('favorites')['characters']:
                        fav_characters.append(f"[{character.get('name')}]({character.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_characters):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_characters = fav_characters[0:i]
                            fav_characters[i-1] = fav_characters[i-1] + '...'
                            break
                    embed.add_field(name='Favorite Characters', value=' | '.join(fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters', value='N/A', inline=False)

                if data.get('favorites')['people']:
                    fav_people = []
                    for people in data.get('favorites')['people']:
                        fav_people.append(f"[{people.get('name')}]({people.get('url')})")
                    total = 0
                    for i, fav in enumerate(fav_people):
                        total += len(fav)+3
                        if total >= 1024:
                            fav_people = fav_people[0:i]
                            fav_people[i-1] = fav_people[i-1] + '...'
                            break
                    embed.add_field(name='Favorite People', value=' | '.join(fav_people), inline=False)
                else:
                    embed.add_field(name='Favorite People', value='N/A', inline=False)

                embed.set_footer(text=f'Provided by https://myanimelist.net/ • Page 2/2')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the MyAnimeList profile.')
                embed.set_footer(text=f'Provided by https://myanimelist.net/ • Page 2/2')
                embeds.append(embed)

            return embeds

        return None

    async def get_kitsu_profile(self, username: str) -> Union[List[discord.Embed], None]:
        """
        Returns a list of Discord embeds with the retrieved Kitsu data about the searched profile.

        Args:
            username (str): The profile name.

        Returns:
            list (Embed): A list of discord embeds.
            None: If no profile was found.
        """
        embeds = []

        try:
            data = await self.bot.kitsu.user(username=username)

        except Exception as e:
            log.exception(e)

            embed = discord.Embed(
                title=f'An error occurred while searching the Kitsu profile `{username}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:

            try:
                if data.get('data')[0].get('attributes').get('createdAt'):
                    createdAt = data.get('data')[0].get('attributes').get('createdAt').split('T')
                    createdAt = createdAt[0]
                else:
                    createdAt = 'N/A'
                if data.get('data')[0].get('attributes').get('updatedAt'):
                    updatedAt = data.get('data')[0].get('attributes').get('updatedAt').split('T')
                    updatedAt = updatedAt[0]
                else:
                    updatedAt = 'N/A'
                if data.get('data')[0].get('attributes').get('location'):
                    location = data.get('data')[0].get('attributes').get('location')
                else:
                    location = 'N/A'
                if data.get('data')[0].get('attributes').get('birthday'):
                    birthday = data.get('data')[0].get('attributes').get('birthday')
                else:
                    birthday = 'N/A'
                if data.get('data')[0].get('attributes').get('gender'):
                    gender = data.get('data')[0].get('attributes').get('gender') \
                        .replace('male', 'Male').replace('feMale', 'Female')
                else:
                    gender = 'N/A'

                embed = discord.Embed(title=f'{data.get("data")[0]["attributes"]["name"]} - Kitsu',
                                      url=f'https://kitsu.io/users/{data.get("data")[0].get("id")}',
                                      color=DEFAULT_EMBED_COLOR, description=f'**Gender:** {gender}\n'
                                                                             f'**Birthday:** {birthday}\n'
                                                                             f'**Location:** {location}\n'
                                                                             f'**Created at:** {createdAt}\n'
                                                                             f'**Updated at:** {updatedAt}\n', )

                if data.get('data')[0].get('attributes').get('avatar'):
                    embed.set_thumbnail(url=data.get('data')[0]['attributes']['avatar']['original'])

                if data.get('data')[0].get('attributes').get('coverImage'):
                    embed.set_image(url=data.get('data')[0]['attributes']['coverImage']['original'])

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
                                            str(datetime.timedelta(seconds=anime_stats['time'])).split(',')
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

                embed.set_footer(text=f'Provided by https://kitsu.io/ • Page 1/1')

                embeds.append(embed)

            except Exception as e:
                log.exception(e)

                embed = discord.Embed(
                    title='Error',
                    color=ERROR_EMBED_COLOR,
                    description='An error occurred while loading the embed for the Kitsu profile.')
                embed.set_footer(text=f'Provided by https://kitsu.io/ • Page 1/1')
                embeds.append(embed)

            return embeds

        return None

    @commands.command(name='anilist', aliases=['al'], usage='anilist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anilist(self, ctx: Context, username: Optional[str] = None):
        """
        Displays information about the given AniList profile such as anime stats, manga stats and favorites.
        """
        async with ctx.channel.typing():
            if username is None:
                username = self.bot.db.select_profile('anilist', ctx.author.id)
            elif username.startswith('<@!'):
                id_ = int(username.replace('<@!', '').replace('>', ''))
                username = self.bot.db.select_profile('anilist', id_)
            else:
                username = username
            if username:
                embeds = await self.get_anilist_profile(username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title=f'The AniList profile `{username}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='No AniList profile set.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='myanimelist', aliases=['mal'], usage='myanimelist [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def myanimelist(self, ctx: Context, username: Optional[str] = None):
        """
        Displays information about the given MyAnimeList profile such as anime stats, manga stats and favorites.
        """
        async with ctx.channel.typing():
            async with ctx.channel.typing():
                if username is None:
                    username = self.bot.db.select_profile('myanimelist', ctx.author.id)
                elif username.startswith('<@!'):
                    id_ = int(username.replace('<@!', '').replace('>', ''))
                    username = self.bot.db.select_profile('myanimelist', id_)
                else:
                    username = username
                if username:
                    embeds = await self.get_myanimelist_profile(username)
                    if embeds:
                        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                        await menu.start(ctx)
                    else:
                        embed = discord.Embed(title=f'The MyAnimeList profile `{username}` could not be found.',
                                              color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title='No MyAnimeList profile set.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)

    @commands.command(name='kitsu', aliases=['k', 'kit'], usage='kitsu [username|@member]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kitsu(self, ctx: Context, username: Optional[str] = None):
        """
        Displays information about the given Kitsu profile such as anime stats, manga stats and favorites!
        """
        async with ctx.channel.typing():
            if username is None:
                username = self.bot.db.select_profile('kitsu', ctx.author.id)
            elif username.startswith('<@!'):
                id_ = int(username.replace('<@!', '').replace('>', ''))
                username = self.bot.db.select_profile('kitsu', id_)
            else:
                username = username
            if username:
                embeds = await self.get_kitsu_profile(username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title=f'The Kitsu profile `{username}` could not be found.',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='No Kitsu profile set.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='setprofile', aliases=['sp', 'setp'], usage='setprofile <al|mal|kitsu> <username>',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def setprofile(self, ctx: Context, site: Optional[str] = None, username: Optional[str] = None):
        """
        Sets an AniList, MyAnimeList or Kitsu profile.
        """
        async with ctx.channel.typing():
            if site:
                if username:
                    if site.lower() == 'anilist' or site.lower() == 'al':
                        await self.set_profile(ctx, 'anilist', username)
                    elif site.lower() == 'myanimelist' or site.lower() == 'mal':
                        await self.set_profile(ctx, 'myanimelist', username)
                    elif site.lower() == 'kitsu':
                        await self.set_profile(ctx, 'kitsu', username)
                    else:
                        ctx.command.reset_cooldown(ctx)
                        raise discord.ext.commands.BadArgument
                elif site.startswith('<@!'):
                    id_ = int(site.replace('<@!', '').replace('>', ''))
                    await self.show_profiles(ctx, id_)
                else:
                    ctx.command.reset_cooldown(ctx)
                    raise discord.ext.commands.BadArgument
            else:
                await self.show_profiles(ctx, ctx.author.id)

    @commands.command(name='removeprofiles', aliases=['rmp'], usage='removeprofiles', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def removeprofiles(self, ctx: Context):
        """
        Removes the set AniList, MyAnimeList and Kitsu profile.
        """
        async with ctx.channel.typing():
            anilist = self.bot.db.select_profile('anilist', ctx.author.id)
            myanimelist = self.bot.db.select_profile('myanimelist', ctx.author.id)
            kitsu = self.bot.db.select_profile('kitsu', ctx.author.id)
            if anilist or myanimelist or kitsu:
                self.bot.db.delete_user(ctx.author.id)
                embed = discord.Embed(title='Removed the set AniList, MyAnimeList and Kitsu profile.',
                                      color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='You have no profile set.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
