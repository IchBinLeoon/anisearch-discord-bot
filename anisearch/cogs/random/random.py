import random

import aiohttp
import discord
import psycopg2
from discord.ext import commands

from anisearch import config
from anisearch.bot import logger
from anisearch.queries import random_query

example_medias = ['anime', 'manga']
example_genres = ['Action', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Slice of Life']


def get_prefix(ctx):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
    prefix = cur.fetchone()[0]
    db.commit()
    cur.close()
    db.close()
    return prefix


class Random(commands.Cog, name='Random'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='random', aliases=['r', 'rndm'], usage='random <anime|manga> <genre>', brief='7s',
                      ignore_extra=False)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def cmd_random(self, ctx, media, *, genre):
        """Displays information about a random anime or manga of the specified genre."""
        if media == 'anime' or media == 'Anime':
            page = random.randrange(1, 10)
            api = 'https://graphql.anilist.co'
            query = random_query.query_anime
            variables = {
                'genre': genre,
                'page': page,
                'amount': 20,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        x = random.randrange(0, 20)
                        if json['data']['Page']['media']:
                            data = json['data']['Page']['media'][x]
                            try:
                                try:
                                    color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                except AttributeError:
                                    color = 0x4169E1
                                if data['title']['english'] is None or data['title']['english'] == \
                                        data['title']['romaji']:
                                    anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                else:
                                    anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                   data['title']['english']),
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                if data['description']:
                                    if len(data['description']) < 1024:
                                        anime_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' '),
                                                              inline=False)
                                    else:
                                        anime_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                                else:
                                    anime_embed.add_field(name='Description', value='-', inline=False)
                                anime_embed.add_field(name='Type', value=data['format'].replace('_', ' ').title()
                                                      .replace('Tv', 'TV')
                                                      .replace('Ova', 'OVA')
                                                      .replace('Ona', 'ONA'),
                                                      inline=True)
                                anime_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                      inline=True)
                                if data['status'].title() == 'Releasing':
                                    if data['nextAiringEpisode']:
                                        if data['episodes']:
                                            anime_embed.add_field(name='Released episodes',
                                                                  value='%s (%s Total)' %
                                                                        (data['nextAiringEpisode']['episode'] - 1,
                                                                         data['episodes']),
                                                                  inline=True)
                                        else:
                                            anime_embed.add_field(name='Released episodes',
                                                                  value=data['nextAiringEpisode']['episode'] - 1,
                                                                  inline=True)
                                    else:
                                        anime_embed.add_field(name='Released episodes',
                                                              value='-',
                                                              inline=True)
                                else:
                                    if data['episodes']:
                                        anime_embed.add_field(name='Episodes', value=data['episodes'], inline=True)
                                    else:
                                        anime_embed.add_field(name='Episodes', value='-', inline=True)
                                if data['season']:
                                    if data['seasonYear']:
                                        anime_embed.add_field(name='Season', value='%s %s' % (data['season'].title(),
                                                                                              data['seasonYear']),
                                                              inline=True)
                                    else:
                                        anime_embed.add_field(name='Season', value=data['season'].title(), inline=True)
                                else:
                                    anime_embed.add_field(name='Season', value='-', inline=True)

                                if data['startDate']['day']:
                                    anime_embed.add_field(name='Start date',
                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                              data['startDate']['month'],
                                                                              data['startDate']['year']),
                                                          inline=True)
                                else:
                                    anime_embed.add_field(name='Start date', value='-', inline=True)
                                if data['endDate']['day']:
                                    anime_embed.add_field(name='End date', value='%s/%s/%s' % (data['endDate']['day'],
                                                                                               data['endDate']['month'],
                                                                                               data['endDate']['year']),
                                                          inline=True)
                                else:
                                    anime_embed.add_field(name='End date', value='-', inline=True)
                                if data['duration']:
                                    if data['episodes'] == 1:
                                        anime_embed.add_field(name='Duration', value=str(data['duration']) + ' min',
                                                              inline=True)
                                    else:
                                        anime_embed.add_field(name='Duration',
                                                              value=str(data['duration']) + ' min each',
                                                              inline=True)
                                else:
                                    anime_embed.add_field(name='Duration', value='-', inline=True)
                                try:
                                    anime_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                          inline=True)
                                except AttributeError:
                                    anime_embed.add_field(name='Source', value='-', inline=True)
                                try:
                                    anime_embed.add_field(name='Studio', value=data['studios']['nodes'][0]['name'],
                                                          inline=True)
                                except IndexError:
                                    anime_embed.add_field(name='Studio', value='-', inline=True)
                                if data['averageScore']:
                                    anime_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                else:
                                    anime_embed.add_field(name='Ø Score', value='-', inline=True)
                                if data['popularity']:
                                    anime_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                else:
                                    anime_embed.add_field(name='Popularity', value='-', inline=True)
                                if data['favourites']:
                                    anime_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                else:
                                    anime_embed.add_field(name='Favourites', value='-', inline=True)
                                if data['genres']:
                                    anime_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                else:
                                    anime_embed.add_field(name='Genres', value='-', inline=False)
                                if data['synonyms']:
                                    anime_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                          inline=False)
                                else:
                                    anime_embed.add_field(name='Synonyms', value='-', inline=True)
                                if data['siteUrl']:
                                    anime_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                else:
                                    anime_embed.add_field(name='AniList Link', value='-', inline=False)
                                if data['idMal']:
                                    anime_embed.add_field(name='MyAnimeList Link',
                                                          value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                          inline=False)
                                else:
                                    anime_embed.add_field(name='MyAnimeList Link', value='-', inline=False)
                                anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=anime_embed)
                                logger.info('Server: %s | Response: Random Anime - %s' % (ctx.guild.name,
                                                                                              data['title'][
                                                                                                        'romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for an anime with the genre `%s`' % genre,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.exception(e)
                        else:
                            page = random.randrange(1, 10)
                            api = 'https://graphql.anilist.co'
                            query = random_query.query_anime_tag
                            variables = {
                                'tag': genre,
                                'page': page,
                                'amount': 20,
                            }
                            async with aiohttp.ClientSession() as session_tag:
                                async with session_tag.post(api, json={'query': query, 'variables': variables}) as rt:
                                    if rt.status == 200:
                                        json = await rt.json()
                                        x = random.randrange(0, 20)
                                        if json['data']['Page']['media']:
                                            data = json['data']['Page']['media'][x]
                                            try:
                                                try:
                                                    color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                                except AttributeError:
                                                    color = 0x4169E1
                                                if data['title']['english'] is None or data['title']['english'] == \
                                                        data['title']['romaji']:
                                                    anime_embed = discord.Embed(title=data['title']['romaji'],
                                                                                color=color,
                                                                                timestamp=ctx.message.created_at)
                                                else:
                                                    anime_embed = discord.Embed(
                                                        title='%s (%s)' % (data['title']['romaji'],
                                                                           data['title']['english']),
                                                        color=color,
                                                        timestamp=ctx.message.created_at)
                                                anime_embed.set_thumbnail(url=data['coverImage']['large'])
                                                if data['description']:
                                                    if len(data['description']) < 1024:
                                                        anime_embed.add_field(name='Description',
                                                                              value=data['description']
                                                                              .replace('<br>', ' ')
                                                                              .replace('</br>', ' ')
                                                                              .replace('<i>', ' ')
                                                                              .replace('</i>', ' '),
                                                                              inline=False)
                                                    else:
                                                        anime_embed.add_field(name='Description',
                                                                              value=data['description']
                                                                              .replace('<br>', ' ')
                                                                              .replace('</br>', ' ')
                                                                              .replace('<i>', ' ')
                                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                                              inline=False)
                                                else:
                                                    anime_embed.add_field(name='Description', value='-', inline=False)
                                                anime_embed.add_field(name='Type',
                                                                      value=data['format'].replace('_', ' ').title()
                                                                      .replace('Tv', 'TV')
                                                                      .replace('Ova', 'OVA')
                                                                      .replace('Ona', 'ONA'),
                                                                      inline=True)
                                                anime_embed.add_field(name='Status',
                                                                      value=data['status'].replace('_', ' ').title(),
                                                                      inline=True)
                                                if data['status'].title() == 'Releasing':
                                                    if data['nextAiringEpisode']:
                                                        if data['episodes']:
                                                            anime_embed.add_field(name='Released episodes',
                                                                                  value='%s (%s Total)' %
                                                                                        (data['nextAiringEpisode'][
                                                                                             'episode'] - 1,
                                                                                         data['episodes']),
                                                                                  inline=True)
                                                        else:
                                                            anime_embed.add_field(name='Released episodes',
                                                                                  value=data['nextAiringEpisode'][
                                                                                            'episode'] - 1,
                                                                                  inline=True)
                                                    else:
                                                        anime_embed.add_field(name='Released episodes',
                                                                              value='-',
                                                                              inline=True)
                                                else:
                                                    if data['episodes']:
                                                        anime_embed.add_field(name='Episodes', value=data['episodes'],
                                                                              inline=True)
                                                    else:
                                                        anime_embed.add_field(name='Episodes', value='-', inline=True)
                                                if data['season']:
                                                    if data['seasonYear']:
                                                        anime_embed.add_field(name='Season',
                                                                              value='%s %s' % (data['season'].title(),
                                                                                               data['seasonYear']),
                                                                              inline=True)
                                                    else:
                                                        anime_embed.add_field(name='Season',
                                                                              value=data['season'].title(), inline=True)
                                                else:
                                                    anime_embed.add_field(name='Season', value='-', inline=True)

                                                if data['startDate']['day']:
                                                    anime_embed.add_field(name='Start date',
                                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                                              data['startDate'][
                                                                                                  'month'],
                                                                                              data['startDate'][
                                                                                                  'year']),
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='Start date', value='-', inline=True)
                                                if data['endDate']['day']:
                                                    anime_embed.add_field(name='End date',
                                                                          value='%s/%s/%s' % (data['endDate']['day'],
                                                                                              data['endDate']['month'],
                                                                                              data['endDate']['year']),
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='End date', value='-', inline=True)
                                                if data['duration']:
                                                    if data['episodes'] == 1:
                                                        anime_embed.add_field(name='Duration',
                                                                              value=str(data['duration']) + ' min',
                                                                              inline=True)
                                                    else:
                                                        anime_embed.add_field(name='Duration',
                                                                              value=str(data['duration']) + ' min each',
                                                                              inline=True)
                                                else:
                                                    anime_embed.add_field(name='Duration', value='-', inline=True)
                                                try:
                                                    anime_embed.add_field(name='Source',
                                                                          value=data['source'].replace('_',
                                                                                                       ' ').title(),
                                                                          inline=True)
                                                except AttributeError:
                                                    anime_embed.add_field(name='Source', value='-', inline=True)
                                                try:
                                                    anime_embed.add_field(name='Studio',
                                                                          value=data['studios']['nodes'][0]['name'],
                                                                          inline=True)
                                                except IndexError:
                                                    anime_embed.add_field(name='Studio', value='-', inline=True)
                                                if data['averageScore']:
                                                    anime_embed.add_field(name='Ø Score', value=data['averageScore'],
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='Ø Score', value='-', inline=True)
                                                if data['popularity']:
                                                    anime_embed.add_field(name='Popularity', value=data['popularity'],
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='Popularity', value='-', inline=True)
                                                if data['favourites']:
                                                    anime_embed.add_field(name='Favourites', value=data['favourites'],
                                                                          inline=True)
                                                else:
                                                    anime_embed.add_field(name='Favourites', value='-', inline=True)
                                                if data['genres']:
                                                    anime_embed.add_field(name='Genres',
                                                                          value=', '.join(data['genres']), inline=False)
                                                else:
                                                    anime_embed.add_field(name='Genres', value='-', inline=False)
                                                if data['synonyms']:
                                                    anime_embed.add_field(name='Synonyms',
                                                                          value=', '.join(data['synonyms']),
                                                                          inline=False)
                                                else:
                                                    anime_embed.add_field(name='Synonyms', value='-', inline=True)
                                                if data['siteUrl']:
                                                    anime_embed.add_field(name='AniList Link', value=data['siteUrl'],
                                                                          inline=False)
                                                else:
                                                    anime_embed.add_field(name='AniList Link', value='-', inline=False)
                                                if data['idMal']:
                                                    anime_embed.add_field(name='MyAnimeList Link',
                                                                          value='https://myanimelist.net/anime/' + str(
                                                                              data['idMal']),
                                                                          inline=False)
                                                else:
                                                    anime_embed.add_field(name='MyAnimeList Link', value='-',
                                                                          inline=False)
                                                anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                                       icon_url=ctx.author.avatar_url)
                                                await ctx.channel.send(embed=anime_embed)
                                                logger.info(
                                                    'Server: %s | Response: Random Anime - %s' % (ctx.guild.name,
                                                                                                  data['title'][
                                                                                                      'romaji']))
                                            except Exception as e:
                                                error_embed = discord.Embed(
                                                    title='An error occurred while searching for an anime with '
                                                          'the genre `%s`' % genre,
                                                    color=0xff0000)
                                                await ctx.channel.send(embed=error_embed)
                                                logger.exception(e)
                                        else:
                                            error_embed = discord.Embed(
                                                title='An anime with the genre `%s` does not exist in the AniList '
                                                      'database' % genre,
                                                color=0xff0000)
                                            await ctx.channel.send(embed=error_embed)
                                            logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                                    else:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for an anime with the genre `%s`'
                                                  % genre,
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.info('Server: %s | Response: Error' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for an anime with the genre `%s`' % genre,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        logger.info('Server: %s | Response: Error' % ctx.guild.name)

        elif media == 'manga' or media == 'Manga':
            page = random.randrange(1, 10)
            api = 'https://graphql.anilist.co'
            query = random_query.query_manga
            variables = {
                'genre': genre,
                'page': page,
                'amount': 20,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        x = random.randrange(0, 20)
                        if json['data']['Page']['media']:
                            data = json['data']['Page']['media'][x]
                            try:
                                try:
                                    color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                except AttributeError:
                                    color = 0x4169E1
                                if data['title']['english'] is None or data['title']['english'] == \
                                        data['title']['romaji']:
                                    manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                else:
                                    manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                   data['title']['english']),
                                                                color=color,
                                                                timestamp=ctx.message.created_at)
                                manga_embed.set_thumbnail(url=data['coverImage']['large'])
                                if data['description']:
                                    if len(data['description']) < 1024:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' '),
                                                              inline=False)
                                    else:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description']
                                                              .replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ')
                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                                else:
                                    manga_embed.add_field(name='Description', value='-', inline=False)
                                manga_embed.add_field(name='Type', value=data['format'].replace('_', ' ').title()
                                                      .replace('Tv', 'TV')
                                                      .replace('Ova', 'OVA')
                                                      .replace('Ona', 'ONA'),
                                                      inline=True)
                                manga_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                      inline=True)
                                if data['chapters']:
                                    if data['volumes']:
                                        manga_embed.add_field(name='Chapters',
                                                              value='%s (%s Volumes)' % (data['chapters'],
                                                                                         data['volumes']),
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters', value='%s' % data['chapters'],
                                                              inline=True)
                                else:
                                    if data['volumes']:
                                        manga_embed.add_field(name='Chapters', value='- (%s Volumes)' % data['volumes'],
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters', value='-', inline=True)
                                if data['startDate']['day']:
                                    manga_embed.add_field(name='Start date',
                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                              data['startDate']['month'],
                                                                              data['startDate']['year']),
                                                          inline=True)
                                else:
                                    manga_embed.add_field(name='Start date', value='-', inline=True)
                                if data['endDate']['day']:
                                    manga_embed.add_field(name='End date', value='%s/%s/%s' % (data['endDate']['day'],
                                                                                               data['endDate']['month'],
                                                                                               data['endDate']['year']),
                                                          inline=True)
                                else:
                                    manga_embed.add_field(name='End date', value='-', inline=True)
                                try:
                                    manga_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                          inline=True)
                                except AttributeError:
                                    manga_embed.add_field(name='Source', value='-', inline=True)
                                if data['averageScore']:
                                    manga_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                else:
                                    manga_embed.add_field(name='Ø Score', value='-', inline=True)
                                if data['popularity']:
                                    manga_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                else:
                                    manga_embed.add_field(name='Popularity', value='-', inline=True)
                                if data['favourites']:
                                    manga_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                else:
                                    manga_embed.add_field(name='Favourites', value='-', inline=True)
                                if data['genres']:
                                    manga_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                else:
                                    manga_embed.add_field(name='Genres', value='-', inline=False)
                                if data['synonyms']:
                                    manga_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                          inline=False)
                                else:
                                    manga_embed.add_field(name='Synonyms', value='-', inline=True)
                                if data['siteUrl']:
                                    manga_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                else:
                                    manga_embed.add_field(name='AniList Link', value='-', inline=False)
                                if data['idMal']:
                                    manga_embed.add_field(name='MyAnimeList Link',
                                                          value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                          inline=False)
                                else:
                                    manga_embed.add_field(name='MyAnimeList Link', value='-', inline=False)
                                manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=manga_embed)
                                logger.info('Server: %s | Response: Random Manga - %s' % (ctx.guild.name,
                                                                                              data['title'][
                                                                                                        'romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for a manga with the genre `%s`' % genre,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                logger.exception(e)
                        else:
                            page = random.randrange(1, 10)
                            api = 'https://graphql.anilist.co'
                            query = random_query.query_manga_tag
                            variables = {
                                'tag': genre,
                                'page': page,
                                'amount': 20,
                            }
                            async with aiohttp.ClientSession() as session_tag:
                                async with session_tag.post(api, json={'query': query, 'variables': variables}) as rt:
                                    if rt.status == 200:
                                        json = await rt.json()
                                        x = random.randrange(0, 20)
                                        if json['data']['Page']['media']:
                                            data = json['data']['Page']['media'][x]
                                            try:
                                                try:
                                                    color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                                                except AttributeError:
                                                    color = 0x4169E1
                                                if data['title']['english'] is None or data['title']['english'] == \
                                                        data['title']['romaji']:
                                                    manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                                color=color,
                                                                                timestamp=ctx.message.created_at)
                                                else:
                                                    manga_embed = discord.Embed(
                                                        title='%s (%s)' % (data['title']['romaji'],
                                                                           data['title']['english']),
                                                        color=color,
                                                        timestamp=ctx.message.created_at)
                                                manga_embed.set_thumbnail(url=data['coverImage']['large'])
                                                if data['description']:
                                                    if len(data['description']) < 1024:
                                                        manga_embed.add_field(name='Description',
                                                                              value=data['description']
                                                                              .replace('<br>', ' ')
                                                                              .replace('</br>', ' ')
                                                                              .replace('<i>', ' ')
                                                                              .replace('</i>', ' '),
                                                                              inline=False)
                                                    else:
                                                        manga_embed.add_field(name='Description',
                                                                              value=data['description']
                                                                              .replace('<br>', ' ')
                                                                              .replace('</br>', ' ')
                                                                              .replace('<i>', ' ')
                                                                              .replace('</i>', ' ')[0:1021] + '...',
                                                                              inline=False)
                                                else:
                                                    manga_embed.add_field(name='Description', value='-', inline=False)
                                                manga_embed.add_field(name='Type',
                                                                      value=data['format'].replace('_', ' ').title()
                                                                      .replace('Tv', 'TV')
                                                                      .replace('Ova', 'OVA')
                                                                      .replace('Ona', 'ONA'),
                                                                      inline=True)
                                                manga_embed.add_field(name='Status',
                                                                      value=data['status'].replace('_', ' ').title(),
                                                                      inline=True)
                                                if data['chapters']:
                                                    if data['volumes']:
                                                        manga_embed.add_field(name='Chapters',
                                                                              value='%s (%s Volumes)' % (
                                                                                  data['chapters'],
                                                                                  data['volumes']),
                                                                              inline=True)
                                                    else:
                                                        manga_embed.add_field(name='Chapters',
                                                                              value='%s' % data['chapters'],
                                                                              inline=True)
                                                else:
                                                    if data['volumes']:
                                                        manga_embed.add_field(name='Chapters',
                                                                              value='- (%s Volumes)' % data['volumes'],
                                                                              inline=True)
                                                    else:
                                                        manga_embed.add_field(name='Chapters', value='-', inline=True)
                                                if data['startDate']['day']:
                                                    manga_embed.add_field(name='Start date',
                                                                          value='%s/%s/%s' % (data['startDate']['day'],
                                                                                              data['startDate'][
                                                                                                  'month'],
                                                                                              data['startDate'][
                                                                                                  'year']),
                                                                          inline=True)
                                                else:
                                                    manga_embed.add_field(name='Start date', value='-', inline=True)
                                                if data['endDate']['day']:
                                                    manga_embed.add_field(name='End date',
                                                                          value='%s/%s/%s' % (data['endDate']['day'],
                                                                                              data['endDate']['month'],
                                                                                              data['endDate']['year']),
                                                                          inline=True)
                                                else:
                                                    manga_embed.add_field(name='End date', value='-', inline=True)
                                                try:
                                                    manga_embed.add_field(name='Source',
                                                                          value=data['source'].replace('_',
                                                                                                       ' ').title(),
                                                                          inline=True)
                                                except AttributeError:
                                                    manga_embed.add_field(name='Source', value='-', inline=True)
                                                if data['averageScore']:
                                                    manga_embed.add_field(name='Ø Score', value=data['averageScore'],
                                                                          inline=True)
                                                else:
                                                    manga_embed.add_field(name='Ø Score', value='-', inline=True)
                                                if data['popularity']:
                                                    manga_embed.add_field(name='Popularity', value=data['popularity'],
                                                                          inline=True)
                                                else:
                                                    manga_embed.add_field(name='Popularity', value='-', inline=True)
                                                if data['favourites']:
                                                    manga_embed.add_field(name='Favourites', value=data['favourites'],
                                                                          inline=True)
                                                else:
                                                    manga_embed.add_field(name='Favourites', value='-', inline=True)
                                                if data['genres']:
                                                    manga_embed.add_field(name='Genres',
                                                                          value=', '.join(data['genres']), inline=False)
                                                else:
                                                    manga_embed.add_field(name='Genres', value='-', inline=False)
                                                if data['synonyms']:
                                                    manga_embed.add_field(name='Synonyms',
                                                                          value=', '.join(data['synonyms']),
                                                                          inline=False)
                                                else:
                                                    manga_embed.add_field(name='Synonyms', value='-', inline=True)
                                                if data['siteUrl']:
                                                    manga_embed.add_field(name='AniList Link', value=data['siteUrl'],
                                                                          inline=False)
                                                else:
                                                    manga_embed.add_field(name='AniList Link', value='-', inline=False)
                                                if data['idMal']:
                                                    manga_embed.add_field(name='MyAnimeList Link',
                                                                          value='https://myanimelist.net/anime/' + str(
                                                                              data['idMal']),
                                                                          inline=False)
                                                else:
                                                    manga_embed.add_field(name='MyAnimeList Link', value='-',
                                                                          inline=False)
                                                manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                                       icon_url=ctx.author.avatar_url)
                                                await ctx.channel.send(embed=manga_embed)
                                                logger.info(
                                                    'Server: %s | Response: Random Manga - %s' % (ctx.guild.name,
                                                                                                  data['title'][
                                                                                                      'romaji']))
                                            except Exception as e:
                                                error_embed = discord.Embed(
                                                    title='An error occurred while searching for a manga with the '
                                                          'genre `%s`' % genre,
                                                    color=0xff0000)
                                                await ctx.channel.send(embed=error_embed)
                                                logger.exception(e)
                                        else:
                                            error_embed = discord.Embed(
                                                title='An manga with the genre `%s` does not exist in the AniList '
                                                      'database' % genre,
                                                color=0xff0000)
                                            await ctx.channel.send(embed=error_embed)
                                            logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                                    else:
                                        error_embed = discord.Embed(
                                            title='An error occurred while searching for a manga with the genre `%s`'
                                                  % genre,
                                            color=0xff0000)
                                        await ctx.channel.send(embed=error_embed)
                                        logger.info('Server: %s | Response: Error' % ctx.guild.name)
                    else:
                        error_embed = discord.Embed(
                            title='An error occurred while searching for a manga with the genre `%s`' % genre,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        logger.info('Server: %s | Response: Error' % ctx.guild.name)
        else:
            prefix = get_prefix(ctx)
            example_media = random.choice(example_medias)
            example_genre = random.choice(example_genres)
            example = '`%srandom %s %s`' % (prefix, example_media, example_genre)
            error_embed = discord.Embed(title='Wrong arguments. Example: %s' % example,
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            await ctx.command.reset_cooldown(ctx)
            logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)
