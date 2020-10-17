from typing import Optional

import aiohttp
import discord
import psycopg2
from discord.ext import commands

import main
from config import config
from modules.anilist import anilist_query


class AniList(commands.Cog, name='AniList'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='anilist', aliases=['al'], usage='anilist [username|@member]', brief='5s',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_anilist(self, ctx, username: Optional[str]):
        """Displays information about the given AniList Profile such as anime stats, manga stats and favorites."""
        db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER,
                              password=config.BD_PASSWORD)
        cur = db.cursor()

        if username is None:
            user_id = ctx.author.id
            try:
                cur.execute('SELECT anilist FROM users WHERE id = %s;', (user_id,))
                anilist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                username = anilist
            except TypeError:
                username = None
                error_embed = discord.Embed(
                    title='You have no AniList Profile linked', color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)

        elif username.startswith('<@!'):
            user_id = int(username.replace('<@!', '').replace('>', ''))
            try:
                cur.execute('SELECT anilist FROM users WHERE id = %s;', (user_id,))
                anilist = cur.fetchone()[0]
                db.commit()
                cur.close()
                db.close()
                username = anilist
            except TypeError:
                username = None
                error_embed = discord.Embed(
                    title='%s has no AniList Profile linked' % self.client.get_user(user_id).name, color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: No Profile linked' % ctx.guild.name)

        else:
            username = username

        if username:
            api = 'https://graphql.anilist.co'
            query = anilist_query.query
            variables = {
                'username': username
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json_data = await r.json()
                        data = json_data['data']['User']
                        try:
                            anilist_embed = discord.Embed(title='%s - AniList' % data['name'], url=data['siteUrl'],
                                                          color=0x4169E1,
                                                          timestamp=ctx.message.created_at)

                            if data['avatar']['large']:
                                anilist_embed.set_thumbnail(url=data['avatar']['large'])

                            try:
                                if len(data['about']) < 1024:
                                    anilist_embed.add_field(name='About',
                                                            value=data['about'], inline=False)
                                else:
                                    anilist_embed.add_field(name='About',
                                                            value=data['about'][0:1021] + '...', inline=False)
                            except TypeError:
                                anilist_embed.add_field(name='About', value='-', inline=False)

                            anime_count = data['statistics']['anime']['count']
                            anime_mean_score = data['statistics']['anime']['meanScore']
                            anime_days_watched = round(data['statistics']['anime']['minutesWatched'] / 60 / 24, 2)
                            anime_episodes_watched = data['statistics']['anime']['episodesWatched']

                            manga_count = data['statistics']['manga']['count']
                            manga_mean_score = data['statistics']['manga']['meanScore']
                            manga_chapters_read = data['statistics']['manga']['chaptersRead']
                            manga_volumes_read = data['statistics']['manga']['volumesRead']

                            anilist_embed.add_field(name='Anime Stats', value=f'Anime Count: {anime_count}\n'
                                                                              f'Mean Score: {anime_mean_score}\n'
                                                                              f'Days Watched: {anime_days_watched}\n'
                                                                              f'Episodes: {anime_episodes_watched}\n',
                                                    inline=True)
                            anilist_embed.add_field(name='Manga Stats', value=f'Manga Count: {manga_count}\n'
                                                                              f'Mean Score: {manga_mean_score}\n'
                                                                              f'Chapters Read: {manga_chapters_read}\n'
                                                                              f'Volumes Read: {manga_volumes_read}\n',
                                                    inline=True)

                            anilist_embed.add_field(name='Anime List',
                                                    value='https://anilist.co/user/%s/animelist' % data['name'],
                                                    inline=False)
                            anilist_embed.add_field(name='Manga List',
                                                    value='https://anilist.co/user/%s/mangalist' % data['name'],
                                                    inline=False)

                            if data['favourites']['anime']['edges']:
                                fav_anime = []
                                x = 0
                                fav_anime_length = int(len(data['favourites']['anime']['edges']))
                                for i in range(0, fav_anime_length - 1):
                                    fav_anime.append(
                                        str('[' + data['favourites']['anime']['edges'][x]['node']['title']['romaji'] +
                                            '](' + data['favourites']['anime']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                fav_anime.append(
                                    str('[' + data['favourites']['anime']['edges'][x]['node']['title']['romaji'] + ']('
                                        + data['favourites']['anime']['edges'][x]['node']['siteUrl'] + ')'))
                                if len(str(fav_anime)) > 1024:
                                    fav_anime = fav_anime[0:5]
                                    fav_anime[4] = str(fav_anime[4]).replace(' |', '...')
                                    fav_anime = ' '.join(fav_anime)
                                else:
                                    fav_anime = ' '.join(fav_anime)
                            else:
                                fav_anime = '-'

                            if data['favourites']['manga']['edges']:
                                fav_manga = []
                                x = 0
                                fav_manga_length = int(len(data['favourites']['manga']['edges']))
                                for i in range(0, fav_manga_length - 1):
                                    fav_manga.append(
                                        str('[' + data['favourites']['manga']['edges'][x]['node']['title']['romaji'] +
                                            '](' + data['favourites']['manga']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                fav_manga.append(
                                    str('[' + data['favourites']['manga']['edges'][x]['node']['title']['romaji'] + ']('
                                        + data['favourites']['manga']['edges'][x]['node']['siteUrl'] + ')'))
                                if len(str(fav_manga)) > 1024:
                                    fav_manga = fav_manga[0:5]
                                    fav_manga[4] = str(fav_manga[4]).replace(' |', '...')
                                    fav_manga = ' '.join(fav_manga)
                                else:
                                    fav_manga = ' '.join(fav_manga)
                            else:
                                fav_manga = '-'

                            if data['favourites']['characters']['edges']:
                                fav_characters = []
                                x = 0
                                fav_characters_length = int(len(data['favourites']['characters']['edges']))
                                for i in range(0, fav_characters_length - 1):
                                    fav_characters.append(
                                        str('[' + data['favourites']['characters']['edges'][x]['node']['name'][
                                            'full'] + ']('
                                            + data['favourites']['characters']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                fav_characters.append(
                                    str('[' + data['favourites']['characters']['edges'][x]['node']['name']['full'] +
                                        '](' + data['favourites']['characters']['edges'][x]['node']['siteUrl'] + ')'))
                                if len(str(fav_characters)) > 1024:
                                    fav_characters = fav_characters[0:5]
                                    fav_characters[4] = str(fav_characters[4]).replace(' |', '...')
                                    fav_characters = ' '.join(fav_characters)
                                else:
                                    fav_characters = ' '.join(fav_characters)
                            else:
                                fav_characters = '-'

                            if data['favourites']['staff']['edges']:
                                fav_staff = []
                                x = 0
                                fav_staff_length = int(len(data['favourites']['staff']['edges']))
                                for i in range(0, fav_staff_length - 1):
                                    fav_staff.append(
                                        str('[' + data['favourites']['staff']['edges'][x]['node']['name']['full'] + ']('
                                            + data['favourites']['staff']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                fav_staff.append(
                                    str('[' + data['favourites']['staff']['edges'][x]['node']['name']['full'] + ']('
                                        + data['favourites']['staff']['edges'][x]['node']['siteUrl'] + ')'))
                                if len(str(fav_staff)) > 1024:
                                    fav_staff = fav_staff[0:5]
                                    fav_staff[4] = str(fav_staff[4]).replace(' |', '...')
                                    fav_staff = ' '.join(fav_staff)
                                else:
                                    fav_staff = ' '.join(fav_staff)
                            else:
                                fav_staff = '-'

                            if data['favourites']['studios']['edges']:
                                fav_studios = []
                                x = 0
                                fav_studios_length = int(len(data['favourites']['studios']['edges']))
                                for i in range(0, fav_studios_length - 1):
                                    fav_studios.append(
                                        str('[' + data['favourites']['studios']['edges'][x]['node']['name'] + ']('
                                            + data['favourites']['studios']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                fav_studios.append(
                                    str('[' + data['favourites']['studios']['edges'][x]['node']['name'] + ']('
                                        + data['favourites']['studios']['edges'][x]['node']['siteUrl'] + ')'))
                                if len(str(fav_studios)) > 1024:
                                    fav_studios = fav_studios[0:5]
                                    fav_studios[4] = str(fav_studios[4]).replace(' |', '...')
                                    fav_studios = ' '.join(fav_studios)
                                else:
                                    fav_studios = ' '.join(fav_studios)
                            else:
                                fav_studios = '-'

                            anilist_embed.add_field(name='Favorite Anime', value=fav_anime, inline=False)
                            anilist_embed.add_field(name='Favorite Manga', value=fav_manga, inline=False)
                            anilist_embed.add_field(name='Favorite Characters', value=fav_characters, inline=False)
                            anilist_embed.add_field(name='Favorite Staff', value=fav_staff, inline=False)
                            anilist_embed.add_field(name='Favorite Studios', value=fav_studios, inline=False)

                            anilist_embed.set_footer(text='Requested by %s' % ctx.author,
                                                     icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anilist_embed)
                            main.logger.info('Server: %s | Response: AniList - %s' % (ctx.guild.name, data['name']))

                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for AniList Profile `%s`' % username,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.exception(e)

                    else:
                        error_embed = discord.Embed(
                            title='The user `%s` cannot be found on AniList' % username,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(AniList(client))
    main.logger.info('Loaded extension AniList')


def teardown():
    main.logger.info('Unloaded extension AniList')
