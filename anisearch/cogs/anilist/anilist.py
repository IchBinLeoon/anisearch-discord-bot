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

from typing import Optional
import discord
from discord.ext import commands, menus
from anisearch.utils.database.profile import select_anilist_profile
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.queries.user_query import SEARCH_USER_QUERY
from anisearch.utils.requests import anilist_request


class AniList(commands.Cog, name='AniList'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_profile_anilist(self, ctx, username):
        embeds = []
        try:
            variables = {'search': username, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_USER_QUERY, variables))
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the AniList Profile '
                                                             '`{}`. Try again.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None:
            data = data['data']['User']
            try:
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                if data['name']:
                    embed.title = data['name']
                if data['siteUrl']:
                    embed.url = data['siteUrl']
                if data['avatar']['large']:
                    embed.set_thumbnail(url=data['avatar']['large'])
                if data['bannerImage']:
                    embed.set_image(url=data['bannerImage'])
                if data['about']:
                    about = data['about'][0:1000] + '...'
                    embed.add_field(name='About', value=about, inline=False)
                anime_count = data['statistics']['anime']['count']
                anime_mean_score = data['statistics']['anime']['meanScore']
                anime_days_watched = round(data['statistics']['anime']['minutesWatched'] / 60 / 24, 2)
                anime_episodes_watched = data['statistics']['anime']['episodesWatched']
                manga_count = data['statistics']['manga']['count']
                manga_mean_score = data['statistics']['manga']['meanScore']
                manga_chapters_read = data['statistics']['manga']['chaptersRead']
                manga_volumes_read = data['statistics']['manga']['volumesRead']
                embed.add_field(name='Anime Stats', value=f'Anime Count: {anime_count}\n'
                                                          f'Mean Score: {anime_mean_score}\n'
                                                          f'Days Watched: {anime_days_watched}\n'
                                                          f'Episodes: {anime_episodes_watched}\n',
                                inline=True)
                embed.add_field(name='Manga Stats', value=f'Manga Count: {manga_count}\n'
                                                          f'Mean Score: {manga_mean_score}\n'
                                                          f'Chapters Read: {manga_chapters_read}\n'
                                                          f'Volumes Read: {manga_volumes_read}\n',
                                inline=True)
                embed.add_field(name='Anime List', value='https://anilist.co/user/%s/animelist' % data['name'],
                                inline=False)
                embed.add_field(name='Manga List', value='https://anilist.co/user/%s/mangalist' % data['name'],
                                inline=False)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the AniList Profile.',
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            try:
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                if data['name']:
                    embed.title = data['name']
                if data['siteUrl']:
                    embed.url = data['siteUrl']
                if data['avatar']['large']:
                    embed.set_thumbnail(url=data['avatar']['large'])
                if data['favourites']['anime']['edges']:
                    fav_anime = []
                    for anime in data['favourites']['anime']['edges']:
                        anime_name = anime['node']['title']['romaji']
                        anime_url = anime['node']['siteUrl']
                        anime_list_object = '[{}]({})'.format(anime_name, anime_url)
                        fav_anime.append(anime_list_object)
                    if len(fav_anime) > 10:
                        fav_anime = fav_anime[0:10]
                        fav_anime[9] = fav_anime[9] + '...'
                    embed.add_field(name='Favorite Anime', value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime', value='-', inline=False)
                if data['favourites']['manga']['edges']:
                    fav_manga = []
                    for manga in data['favourites']['manga']['edges']:
                        manga_name = manga['node']['title']['romaji']
                        manga_url = manga['node']['siteUrl']
                        manga_list_object = '[{}]({})'.format(manga_name, manga_url)
                        fav_manga.append(manga_list_object)
                    if len(fav_manga) > 10:
                        fav_manga = fav_manga[0:10]
                        fav_manga[9] = fav_manga[9] + '...'
                    embed.add_field(name='Favorite Manga', value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Characters', value='-', inline=False)
                if data['favourites']['characters']['edges']:
                    fav_characters = []
                    for character in data['favourites']['characters']['edges']:
                        character_name = character['node']['name']['full']
                        character_url = character['node']['siteUrl']
                        character_list_object = '[{}]({})'.format(character_name, character_url)
                        fav_characters.append(character_list_object)
                    if len(fav_characters) > 10:
                        fav_characters = fav_characters[0:10]
                        fav_characters[9] = fav_characters[9] + '...'
                    embed.add_field(name='Favorite Characters', value=' | '.join(fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters', value='-', inline=False)
                if data['favourites']['staff']['edges']:
                    fav_staff = []
                    for staff in data['favourites']['staff']['edges']:
                        staff_name = staff['node']['name']['full']
                        staff_url = staff['node']['siteUrl']
                        staff_list_object = '[{}]({})'.format(staff_name, staff_url)
                        fav_staff.append(staff_list_object)
                    if len(fav_staff) > 10:
                        fav_staff = fav_staff[0:10]
                        fav_staff[9] = fav_staff[9] + '...'
                    embed.add_field(name='Favorite Staff', value=' | '.join(fav_staff), inline=False)
                else:
                    embed.add_field(name='Favorite Staff', value='-', inline=False)
                if data['favourites']['studios']['edges']:
                    fav_studio = []
                    for studio in data['favourites']['studios']['edges']:
                        studio_name = studio['node']['name']
                        studio_url = studio['node']['siteUrl']
                        studio_list_object = '[{}]({})'.format(studio_name, studio_url)
                        fav_studio.append(studio_list_object)
                    if len(fav_studio) > 10:
                        fav_studio = fav_studio[0:10]
                        fav_studio[9] = fav_studio[9] + '...'
                    embed.add_field(name='Favorite Studio', value=' | '.join(fav_studio), inline=False)
                else:
                    embed.add_field(name='Favorite Studio', value='-', inline=False)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the AniList Profile.',
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
        return embeds

    @commands.command(name='anilist', aliases=['al'], usage='anilist [username|@member]', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_anilist(self, ctx, username: Optional[str]):
        """Displays information about the given AniList Profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            if username is None:
                user_id = ctx.author.id
                try:
                    username = select_anilist_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            elif username.startswith('<@!'):
                user_id = int(username.replace('<@!', '').replace('>', ''))
                try:
                    username = select_anilist_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            else:
                username = username
            if username:
                embeds = await self._search_profile_anilist(ctx, username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title='The AniList Profile `{}` could not be found.'.format(username),
                                          color=0xff0000)
                    await ctx.channel.send(embed=embed)
            else:
                error_embed = discord.Embed(title='No AniList Profile set.', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
