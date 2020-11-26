from typing import Optional

import discord
from discord.ext import commands, menus

from anisearch.utils.database.profile import select_myanimelist_profile
from anisearch.utils.formats import description_parser
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.requests import myanimelist_request


class MyAnimeList(commands.Cog, name='MyAnimeList'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_profile_myanimelist(self, ctx, username):
        embeds = []
        try:
            user = await myanimelist_request('user', username)
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the MyAnimeList Profile'
                                                             ' `{}`. Try again.'.format(username),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if user is not None:
            try:
                if user.get('last_online'):
                    last_online = user.get('last_online').__str__().replace("-", "/").replace("T", " ").replace("+",
                                                                                                                " +")
                else:
                    last_online = '-'
                if user.get('gender'):
                    gender = user.get('gender').__str__().replace('None', '-')
                else:
                    gender = '-'
                if user.get('birthday'):
                    birthday = user.get('birthday')
                else:
                    birthday = '-'
                if user.get('location'):
                    location = user.get('location')
                else:
                    location = '-'
                if user.get('joined'):
                    joined = user.get('joined').__str__().replace('T00:00:00+00:00', ' ').replace('-', '/')
                else:
                    joined = '-'
                anime = user.get('anime_stats')
                manga = user.get('manga_stats')
                anime_days_watched = anime.get('days_watched')
                anime_mean_score = anime.get('mean_score')
                anime_watching = anime.get('watching')
                anime_completed = anime.get('completed')
                anime_on_hold = anime.get('on_hold')
                anime_dropped = anime.get('dropped')
                anime_plan_to_watch = anime.get('plan_to_watch')
                anime_total_entries = anime.get('total_entries')
                anime_rewatched = anime.get('rewatched')
                anime_episodes_watched = anime.get('episodes_watched')
                manga_days_read = manga.get('days_read')
                manga_mean_score = manga.get('mean_score')
                manga_reading = manga.get('reading')
                manga_completed = manga.get('completed')
                manga_on_hold = manga.get('on_hold')
                manga_dropped = manga.get('dropped')
                manga_plan_to_read = manga.get('plan_to_read')
                manga_reread = manga.get('reread')
                manga_total_entries = manga.get('total_entries')
                manga_chapters_read = manga.get('chapters_read')
                manga_volumes_read = manga.get('volumes_read')
                embed = discord.Embed(title='{} - MyAnimeList'.format(user.get('username')),
                                      description=f'**Last Online:** {last_online}\n'
                                                  f'**Gender:** {gender}\n'
                                                  f'**Birthday:** {birthday}\n'
                                                  f'**Location:** {location}\n'
                                                  f'**Joined:** {joined}\n',
                                      url=user.get('url'),
                                      color=0x4169E1, timestamp=ctx.message.created_at)
                if user.get('image_url'):
                    embed.set_thumbnail(url=user.get('image_url'))
                if user.get('about'):
                    about = user.get('about')[0:1000] + '...'
                    embed.add_field(name='About', value=about, inline=False)
                embed.add_field(name='Anime Stats', value=f'Days Watched: {anime_days_watched}\n'
                                                          f'Mean Score: {anime_mean_score}\n'
                                                          f'Watching: {anime_watching}\n'
                                                          f'Completed: {anime_completed}\n'
                                                          f'On-Hold: {anime_on_hold}\n'
                                                          f'Dropped: {anime_dropped}\n'
                                                          f'Plan to Watch: {anime_plan_to_watch}\n'
                                                          f'Total Entries: {anime_total_entries}\n'
                                                          f'Rewatched: {anime_rewatched}\n'
                                                          f'Episodes: {anime_episodes_watched}\n',
                                inline=True)
                embed.add_field(name='Manga Stats', value=f'Days Read: {manga_days_read}\n'
                                                          f'Mean Score: {manga_mean_score}\n'
                                                          f'Reading: {manga_reading}\n'
                                                          f'Completed: {manga_completed}\n'
                                                          f'On-Hold: {manga_on_hold}\n'
                                                          f'Dropped: {manga_dropped}\n'
                                                          f'Plan to Read: {manga_plan_to_read}\n'
                                                          f'Reread: {manga_reread}\n'
                                                          f'Total Entries: {manga_total_entries}\n'
                                                          f'Chapters Read: {manga_chapters_read}\n'
                                                          f'Volumes Read: {manga_volumes_read}\n',
                                inline=True)
                embed.add_field(name='Anime List',
                                value='https://myanimelist.net/animelist/{}'.format(user.get('username')),
                                inline=False)
                embed.add_field(name='Manga List',
                                value='https://myanimelist.net/mangalist/{}'.format(user.get('username')),
                                inline=False)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the MyAnimeList Profile.',
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            try:
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                embed.title = user.get('username')
                embed.url = user.get('url')
                if user.get('image_url'):
                    embed.set_thumbnail(url=user.get('image_url'))
                if user.get('favorites')['anime']:
                    favorite_anime = user.get('favorites')['anime']
                    fav_anime = []
                    for anime in favorite_anime:
                        anime_name = anime.get('name')
                        anime_url = anime.get('url')
                        anime_list_object = '[{}]({})'.format(anime_name, anime_url)
                        fav_anime.append(anime_list_object)
                    embed.add_field(name='Favorite Anime', value=' | '.join(fav_anime), inline=False)
                else:
                    embed.add_field(name='Favorite Anime', value='-', inline=False)
                if user.get('favorites')['manga']:
                    favorite_manga = user.get('favorites')['manga']
                    fav_manga = []
                    for manga in favorite_manga:
                        manga_name = manga.get('name')
                        manga_url = manga.get('url')
                        manga_list_object = '[{}]({})'.format(manga_name, manga_url)
                        fav_manga.append(manga_list_object)
                    embed.add_field(name='Favorite Manga', value=' | '.join(fav_manga), inline=False)
                else:
                    embed.add_field(name='Favorite Manga', value='-', inline=False)
                if user.get('favorites')['characters']:
                    favorite_characters = user.get('favorites')['characters']
                    fav_characters = []
                    for character in favorite_characters:
                        character_name = character.get('name')
                        character_url = character.get('url')
                        character_list_object = '[{}]({})'.format(character_name, character_url)
                        fav_characters.append(character_list_object)
                    embed.add_field(name='Favorite Characters', value=' | '.join(fav_characters), inline=False)
                else:
                    embed.add_field(name='Favorite Characters', value='-', inline=False)
                if user.get('favorites')['people']:
                    favorite_people = user.get('favorites')['people']
                    fav_people = []
                    for people in favorite_people:
                        people_name = people.get('name')
                        people_url = people.get('url')
                        people_list_object = '[{}]({})'.format(people_name, people_url)
                        fav_people.append(people_list_object)
                    embed.add_field(name='Favorite People', value=' | '.join(fav_people), inline=False)
                else:
                    embed.add_field(name='Favorite People', value='-', inline=False)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                 'the MyAnimeList Profile.',
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                embeds.append(embed)
        return embeds

    @commands.command(name='myanimelist', aliases=['mal'], usage='myanimelist [username|@member]', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_myanimelist(self, ctx, username: Optional[str]):
        """Displays information about the given MyAnimeList Profile such as anime stats, manga stats and favorites."""
        async with ctx.channel.typing():
            if username is None:
                user_id = ctx.author.id
                try:
                    username = select_myanimelist_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            elif username.startswith('<@!'):
                user_id = int(username.replace('<@!', '').replace('>', ''))
                try:
                    username = select_myanimelist_profile(user_id)
                except Exception as exception:
                    logger.exception(exception)
                    username = None
            else:
                username = username
            if username:
                embeds = await self._search_profile_myanimelist(ctx, username)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title='The MyAnimeList Profile `{}` could not be found.'.format(username),
                                          color=0xff0000)
                    await ctx.channel.send(embed=embed)
            else:
                error_embed = discord.Embed(title='No MyAnimeList Profile set.', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
