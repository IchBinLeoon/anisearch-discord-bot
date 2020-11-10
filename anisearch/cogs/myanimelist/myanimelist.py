from typing import Optional

import discord
import psycopg2
from discord.ext import commands
from jikanpy import AioJikan

from anisearch import config
from anisearch.bot import logger


class MyAnimeList(commands.Cog, name='MyAnimeList'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='myanimelist', aliases=['mal'], usage='myanimelist [username|@member]', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_myanimelist(self, ctx, username: Optional[str]):
        """Displays information about the given MyAnimeList Profile such as anime stats, manga stats and favorites."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()

        if username is None:
            user_id = ctx.author.id
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                myanimelist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                username = myanimelist
            except TypeError:
                username = None
                error_embed = discord.Embed(
                    title='You have no MyAnimeList Profile linked', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)

        elif username.startswith('<@!'):
            user_id = int(username.replace('<@!', '').replace('>', ''))
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                myanimelist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                username = myanimelist
            except TypeError:
                username = None
                error_embed = discord.Embed(
                    title='%s has no MyAnimeList Profile linked' % self.client.get_user(user_id).name, color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)

        else:
            username = username

        if username:

            aio_jikan = AioJikan()

            try:

                user = await aio_jikan.user(username=username)

                try:
                    if user.get('last_online') is not None:
                        last_online = user.get('last_online').__str__().replace("-", "/").replace("T", " ").replace("+",
                                                                                                                    " +")
                    else:
                        last_online = '-'
                    if user.get('gender') is not None:
                        gender = user.get('gender').__str__().replace('None', '-')
                    else:
                        gender = '-'
                    if user.get('birthday') is not None:
                        birthday = user.get('birthday')
                    else:
                        birthday = '-'
                    if user.get('location') is not None:
                        location = user.get('location')
                    else:
                        location = '-'
                    if user.get('joined') is not None:
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

                    myanimelist_embed = discord.Embed(title=' %s - MyAnimeList' % user.get('username'),
                                                      description=f'**Last Online:** {last_online}\n'
                                                                  f'**Gender:** {gender}\n'
                                                                  f'**Birthday:** {birthday}\n'
                                                                  f'**Location:** {location}\n'
                                                                  f'**Joined:** {joined}\n',
                                                      url=user.get('url'),
                                                      color=0x4169E1, timestamp=ctx.message.created_at)
                    if user.get('image_url'):
                        myanimelist_embed.set_thumbnail(url=user.get('image_url'))
                    try:
                        if len(user.get('about')) < 1024:
                            myanimelist_embed.add_field(name='About',
                                                        value=user.get('about'), inline=False)
                        else:
                            myanimelist_embed.add_field(name='About',
                                                        value=user.get('about')[0:1021] + '...', inline=False)
                    except TypeError:
                        myanimelist_embed.add_field(name='About', value='-', inline=False)
                    myanimelist_embed.add_field(name='Anime Stats', value=f'Days Watched: {anime_days_watched}\n'
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
                    myanimelist_embed.add_field(name='Manga Stats', value=f'Days Read: {manga_days_read}\n'
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
                    myanimelist_embed.add_field(name='Anime List',
                                                value='https://myanimelist.net/animelist/%s' % user.get('username'),
                                                inline=False)
                    myanimelist_embed.add_field(name='Manga List',
                                                value='https://myanimelist.net/mangalist/%s' % user.get('username'),
                                                inline=False)

                    favorite_anime = user.get('favorites')['anime']
                    favorite_manga = user.get('favorites')['manga']
                    favorite_characters = user.get('favorites')['characters']
                    favorite_people = user.get('favorites')['people']

                    if favorite_anime:
                        fav_anime = []
                        x = 0
                        fav_anime_length = int(len(favorite_anime))
                        for i in range(0, fav_anime_length - 1):
                            fav_anime.append(str('[' + favorite_anime[x].get('name') + ']('
                                                 + favorite_anime[x].get('url') + ') | '))
                            x = x + 1
                        fav_anime.append(str('[' + favorite_anime[x].get('name') + ']('
                                             + favorite_anime[x].get('url') + ')'))
                        fav_anime = fav_anime.__str__()[1:-1].replace("'", "").replace(',', '')
                    else:
                        fav_anime = '-'

                    if favorite_manga:
                        fav_manga = []
                        x = 0
                        fav_manga_length = int(len(favorite_manga))
                        for i in range(0, fav_manga_length - 1):
                            fav_manga.append(str('[' + favorite_manga[x].get('name') + ']('
                                                 + favorite_manga[x].get('url') + ') | '))
                            x = x + 1
                        fav_manga.append(str('[' + favorite_manga[x].get('name') + ']('
                                             + favorite_manga[x].get('url') + ')'))
                        fav_manga = fav_manga.__str__()[1:-1].replace("'", "").replace(',', '')
                    else:
                        fav_manga = '-'

                    if favorite_characters:
                        fav_characters = []
                        x = 0
                        fav_characters_length = int(len(favorite_characters))
                        for i in range(0, fav_characters_length - 1):
                            fav_characters.append(str('[' + favorite_characters[x].get('name') + ']('
                                                      + favorite_characters[x].get('url') + ') | '))
                            x = x + 1
                        fav_characters.append(str('[' + favorite_characters[x].get('name') + ']('
                                                  + favorite_characters[x].get('url') + ')'))
                        fav_characters = fav_characters.__str__()[1:-1].replace("'", "").replace(',', '')
                    else:
                        fav_characters = '-'

                    if favorite_people:
                        fav_people = []
                        x = 0
                        fav_people_length = int(len(favorite_people))
                        for i in range(0, fav_people_length - 1):
                            fav_people.append(str('[' + favorite_people[x].get('name') + ']('
                                                  + favorite_people[x].get('url') + ') | '))
                            x = x + 1
                        fav_people.append(str('[' + favorite_people[x].get('name') + '](' +
                                              favorite_people[x].get('url') + ')'))
                        fav_people = fav_people.__str__()[1:-1].replace("'", "").replace(',', '')
                    else:
                        fav_people = '-'

                    myanimelist_embed.add_field(name='Favorite Anime', value=fav_anime, inline=False)
                    myanimelist_embed.add_field(name='Favorite Manga', value=fav_manga, inline=False)
                    myanimelist_embed.add_field(name='Favorite Characters', value=fav_characters, inline=False)
                    myanimelist_embed.add_field(name='Favorite People', value=fav_people, inline=False)

                    myanimelist_embed.set_footer(text='Requested by %s' % ctx.author,
                                                 icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=myanimelist_embed)
                    logger.info(
                        'Server: %s | Response: MyAnimeList - %s' % (ctx.guild.name, user.get('username')))

                except Exception as e:
                    error_embed = discord.Embed(
                        title='An error occurred while searching for MyAnimeList Profile `%s`' % username,
                        color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    logger.exception(e)

            except:
                error_embed = discord.Embed(
                    title='The user `%s` cannot be found on MyAnimeList'
                          % username,
                    color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                logger.info('Server: %s | Response: Not found' % ctx.guild.name)

            await aio_jikan.close()
