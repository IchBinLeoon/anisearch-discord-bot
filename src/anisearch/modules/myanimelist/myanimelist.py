from typing import Optional

import discord
import psycopg2
from discord.ext import commands
import requests

import main
from config import config


class MyAnimeList(commands.Cog, name='MyAnimeList'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='myanimelist', aliases=['mal'], ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_myanimelist(self, ctx, profilename: Optional[str]):
        """Displays information about a MyAnimeList Profile."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()
        if profilename is None:
            user_id = ctx.author.id
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                myanimelist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                profilename = myanimelist
            except TypeError:
                profilename = None
                error_embed = discord.Embed(
                    title='You have no MyAnimeList Profile linked', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)
        elif profilename.startswith('<@!'):
            user_id = int(profilename.replace('<@!', '').replace('>', ''))
            try:
                cur.execute('SELECT myanimelist FROM users WHERE id = %s;', (user_id,))
                myanimelist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                profilename = myanimelist
            except TypeError:
                profilename = None
                error_embed = discord.Embed(
                    title='%s has no MyAnimeList Profile linked' % self.client.get_user(user_id).name, color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)
        else:
            profilename = profilename
        if profilename:
            data = requests.get('https://api.jikan.moe/v3/user/%s/profile' % profilename).json()
            try:
                if data['status']:
                    error_embed = discord.Embed(
                        title='The user `%s` cannot be found on MyAnimeList'
                              % profilename,
                        color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
            except KeyError:
                if data['last_online'] is not None:
                    last_online = data['last_online'].__str__().replace("-", "/").replace("T", " ").replace("+", " +")
                else:
                    last_online = 'N/A'
                if ['gender'] is not None:
                    gender = data['gender'].__str__().replace('None', 'N/A')
                else:
                    gender = 'N/A'
                if data['birthday'] is not None:
                    birthday = data['birthday']
                else:
                    birthday = 'N/A'
                if data['location'] is not None:
                    location = data['location']
                else:
                    location = 'N/A'
                if data['joined'] is not None:
                    joined = data['joined'].__str__().replace('T00:00:00+00:00', ' ').replace('-', '/')
                else:
                    joined = 'N/A'
                anime_days_watched = data['anime_stats']['days_watched']
                anime_mean_score = data['anime_stats']['mean_score']
                anime_watching = data['anime_stats']['watching']
                anime_completed = data['anime_stats']['completed']
                anime_on_hold = data['anime_stats']['on_hold']
                anime_dropped = data['anime_stats']['dropped']
                anime_plan_to_watch = data['anime_stats']['plan_to_watch']
                anime_total_entries = data['anime_stats']['total_entries']
                anime_rewatched = data['anime_stats']['rewatched']
                anime_episodes_watched = data['anime_stats']['episodes_watched']
                manga_days_read = data['manga_stats']['days_read']
                manga_mean_score = data['manga_stats']['mean_score']
                manga_reading = data['manga_stats']['reading']
                manga_completed = data['manga_stats']['completed']
                manga_on_hold = data['manga_stats']['on_hold']
                manga_dropped = data['manga_stats']['dropped']
                manga_plan_to_read = data['manga_stats']['plan_to_read']
                manga_reread = data['manga_stats']['reread']
                manga_total_entries = data['manga_stats']['total_entries']
                manga_chapters_read = data['manga_stats']['chapters_read']
                manga_volumes_read = data['manga_stats']['volumes_read']
                myanimelist_embed = discord.Embed(title=' %s - MyAnimeList' % data['username'],
                                                  description=f'**Last Online:** {last_online}\n'
                                                              f'**Gender:** {gender}\n'
                                                              f'**Birthday:** {birthday}\n'
                                                              f'**Location:** {location}\n'
                                                              f'**Joined:** {joined}\n',
                                                  url=data['url'],
                                                  color=0x4169E1, timestamp=ctx.message.created_at)
                if data['image_url']:
                    myanimelist_embed.set_thumbnail(url=data['image_url'])
                try:
                    if len(data['about']) < 1024:
                        myanimelist_embed.add_field(name='About',
                                                    value=data['about'], inline=False)
                    else:
                        myanimelist_embed.add_field(name='About',
                                                    value=data['about'][0:1021] + '...', inline=False)
                except TypeError:
                    myanimelist_embed.add_field(name='About', value='N/A', inline=False)
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
                                            value='https://myanimelist.net/animelist/%s' % data['username'],
                                            inline=False)
                myanimelist_embed.add_field(name='Manga List',
                                            value='https://myanimelist.net/mangalist/%s' % data['username'],
                                            inline=False)
                if data['favorites']['anime']:
                    fav_anime = []
                    x = 0
                    fav_anime_length = int(len(data['favorites']['anime']))
                    for i in range(0, fav_anime_length - 1):
                        fav_anime.append(str('[' + data['favorites']['anime'][x]['name'] + ']('
                                             + data['favorites']['anime'][x]['url'] + ') | '))
                        x = x + 1
                    fav_anime.append(str('[' + data['favorites']['anime'][x]['name'] + ']('
                                         + data['favorites']['anime'][x]['url'] + ')'))
                    fav_anime = fav_anime.__str__()[1:-1].replace("'", "").replace(',', '')
                else:
                    fav_anime = 'N/A'
                if data['favorites']['manga']:
                    fav_manga = []
                    x = 0
                    fav_manga_length = int(len(data['favorites']['manga']))
                    for i in range(0, fav_manga_length - 1):
                        fav_manga.append(str('[' + data['favorites']['manga'][x]['name'] + ']('
                                             + data['favorites']['manga'][x]['url'] + ') | '))
                        x = x + 1
                    fav_manga.append(str('[' + data['favorites']['manga'][x]['name'] + ']('
                                         + data['favorites']['manga'][x]['url'] + ')'))
                    fav_manga = fav_manga.__str__()[1:-1].replace("'", "").replace(',', '')
                else:
                    fav_manga = 'N/A'
                if data['favorites']['characters']:
                    fav_characters = []
                    x = 0
                    fav_characters_length = int(len(data['favorites']['characters']))
                    for i in range(0, fav_characters_length - 1):
                        fav_characters.append(str('[' + data['favorites']['characters'][x]['name'] + ']('
                                                  + data['favorites']['characters'][x]['url'] + ') | '))
                        x = x + 1
                    fav_characters.append(str('[' + data['favorites']['characters'][x]['name'] + ']('
                                              + data['favorites']['characters'][x]['url'] + ')'))
                    fav_characters = fav_characters.__str__()[1:-1].replace("'", "").replace(',', '')
                else:
                    fav_characters = 'N/A'
                if data['favorites']['people']:
                    fav_people = []
                    x = 0
                    fav_people_length = int(len(data['favorites']['people']))
                    for i in range(0, fav_people_length - 1):
                        fav_people.append(str('[' + data['favorites']['people'][x]['name'] + ']('
                                              + data['favorites']['people'][x]['url'] + ') | '))
                        x = x + 1
                    fav_people.append(str('[' + data['favorites']['people'][x]['name'] + '](' +
                                          data['favorites']['people'][x]['url'] + ')'))
                    fav_people = fav_people.__str__()[1:-1].replace("'", "").replace(',', '')
                else:
                    fav_people = 'N/A'
                myanimelist_embed.add_field(name='Favorite Anime', value=fav_anime, inline=False)
                myanimelist_embed.add_field(name='Favorite Manga', value=fav_manga, inline=False)
                myanimelist_embed.add_field(name='Favorite Characters', value=fav_characters, inline=False)
                myanimelist_embed.add_field(name='Favorite People', value=fav_people, inline=False)
                myanimelist_embed.set_footer(text='Requested by %s' % ctx.author,
                                             icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=myanimelist_embed)
                main.logger.info('Server: %s | Response: MyAnimeList - %s' % (ctx.guild.name, data['username']))


def setup(client):
    client.add_cog(MyAnimeList(client))
    main.logger.info('Loaded extension MyAnimeList')


def teardown():
    main.logger.info('Unloaded extension MyAnimeList')
