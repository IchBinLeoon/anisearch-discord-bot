import random

import aiohttp
import discord
from discord.ext import commands

import main
from modules.random import random_query


class Random(commands.Cog, name='Random'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='random', aliases=['rndm'], ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_random(self, ctx, media, genre):
        """Shows a random anime or manga of the specified genre."""
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
                                if data['title']['english'] is None or data['title']['english'] == \
                                        data['title']['romaji']:
                                    random_embed = discord.Embed(title=data['title']['romaji'],
                                                                 color=0x4169E1,
                                                                 timestamp=ctx.message.created_at)
                                else:
                                    random_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                    data['title']['english']),
                                                                 color=0x4169E1,
                                                                 timestamp=ctx.message.created_at)
                                random_embed.set_thumbnail(url=data['coverImage']['large'])
                                if len(data['description']) < 1024:
                                    random_embed.add_field(name='Description',
                                                           value=data['description'].replace('<br>', ' ').replace(
                                                               '</br>', ' ')
                                                           .replace('<i>', ' ').replace('</i>', ' '), inline=False)
                                else:
                                    random_embed.add_field(name='Description',
                                                           value=data['description'].replace('<br>', ' ').replace(
                                                               '</br>', ' ')
                                                           .replace('<i>', ' ').replace('</i>', ' ')[0:1021] + '...',
                                                           inline=False)
                                if data['synonyms']:
                                    random_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                           inline=True)
                                else:
                                    random_embed.add_field(name='Synonyms', value='-', inline=True)
                                random_embed.add_field(name='Type',
                                                       value=data['format'].replace('_', ' ').title().replace('Tv',
                                                                                                              'TV'),
                                                       inline=True)
                                if data['episodes'] is None:
                                    random_embed.add_field(name='Episodes', value='N/A',
                                                           inline=True)
                                else:
                                    random_embed.add_field(name='Episodes', value=data['episodes'],
                                                           inline=True)
                                if data['episodes'] == 1:
                                    random_embed.add_field(name='Duration', value=str(data['duration']) + ' min',
                                                           inline=True)
                                else:
                                    random_embed.add_field(name='Duration', value=str(data['duration']) + ' min each',
                                                           inline=True)
                                random_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                       inline=True)
                                random_embed.add_field(name='Start date',
                                                       value='%s/%s/%s' % (data['startDate']['day'],
                                                                           data['startDate']['month'],
                                                                           data['startDate']['year']), inline=True)
                                if data['endDate']['day'] is None:
                                    if data['nextAiringEpisode'] is None:
                                        random_embed.add_field(name='Released episodes', value='N/A',
                                                               inline=True)
                                    else:
                                        random_embed.add_field(name='Released episodes',
                                                               value=data['nextAiringEpisode']['episode'] - 1,
                                                               inline=True)
                                else:
                                    random_embed.add_field(name='End date',
                                                           value='%s/%s/%s' % (data['endDate']['day'],
                                                                               data['endDate']['month'],
                                                                               data['endDate']['year']), inline=True)
                                try:
                                    random_embed.add_field(name='Studio', value=data['studios']['nodes'][0]['name'],
                                                           inline=True)
                                except IndexError:
                                    random_embed.add_field(name='Studio', value='N/A',
                                                           inline=True)
                                random_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                random_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                random_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                try:
                                    random_embed.add_field(name='Source',
                                                           value=data['source'].replace('_', ' ').title(),
                                                           inline=True)
                                except AttributeError:
                                    random_embed.add_field(name='Source', value='N/A',
                                                           inline=True)
                                random_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                random_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                random_embed.add_field(name='MyAnimeList Link',
                                                       value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                       inline=False)
                                random_embed.set_footer(text='Requested by %s' % ctx.author,
                                                        icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=random_embed)
                                main.logger.info('Server: %s | Response: Random Anime - %s' % (ctx.guild.name,
                                                                                               data['title']['romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for an anime with the genre `%s`' % genre,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='An anime with the genre `%s` does not exist in the AniList database' % genre,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
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
                                if data['title']['english'] is None or data['title']['english'] == \
                                        data['title']['romaji']:
                                    manga_embed = discord.Embed(title=data['title']['romaji'],
                                                                color=0x4169E1,
                                                                timestamp=ctx.message.created_at)
                                else:
                                    manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                                   data['title']['english']),
                                                                color=0x4169E1,
                                                                timestamp=ctx.message.created_at)
                                manga_embed.set_thumbnail(url=data['coverImage']['large'])
                                if data['description']:
                                    if len(data['description']) < 1024:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description'].replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ').replace('</i>', ' '), inline=False)
                                    else:
                                        manga_embed.add_field(name='Description',
                                                              value=data['description'].replace('<br>', ' ')
                                                              .replace('</br>', ' ')
                                                              .replace('<i>', ' ').replace('</i>', ' ')[0:1021] + '...',
                                                              inline=False)
                                else:
                                    manga_embed.add_field(name='Description',
                                                          value='N/A', inline=False)
                                if data['synonyms']:
                                    manga_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']),
                                                          inline=True)
                                else:
                                    manga_embed.add_field(name='Synonyms', value='-', inline=True)
                                manga_embed.add_field(name='Type',
                                                      value=data['format'].replace('_', ' ').title().replace('Tv',
                                                                                                             'TV'),
                                                      inline=True)
                                if data['chapters'] is None:
                                    if data['volumes'] is None:
                                        manga_embed.add_field(name='Chapters', value='N/A Chapters\n(N/A Volumes)',
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters',
                                                              value='N/A Chapters\n(%s Volumes)' % data['volumes'],
                                                              inline=True)
                                else:
                                    if data['volumes'] is None:
                                        manga_embed.add_field(name='Chapters',
                                                              value='%s Chapters\n(N/A Volumes)' % data['chapters'],
                                                              inline=True)
                                    else:
                                        manga_embed.add_field(name='Chapters',
                                                              value='%s Chapters\n(%s Volumes)' % (
                                                                  data['chapters'], data['volumes']),
                                                              inline=True)
                                manga_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                      inline=True)
                                manga_embed.add_field(name='Start date',
                                                      value='%s/%s/%s' % (data['startDate']['day'],
                                                                          data['startDate']['month'],
                                                                          data['startDate']['year']), inline=True)
                                if data['endDate']['day']:
                                    manga_embed.add_field(name='End date',
                                                          value='%s/%s/%s' % (data['endDate']['day'],
                                                                              data['endDate']['month'],
                                                                              data['endDate']['year']), inline=True)
                                manga_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                                manga_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                                manga_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                                try:
                                    manga_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                          inline=True)
                                except AttributeError:
                                    manga_embed.add_field(name='Source', value='N/A',
                                                          inline=True)
                                if data['genres']:
                                    manga_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                                else:
                                    manga_embed.add_field(name='Genres', value='N/A', inline=False)
                                manga_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                                manga_embed.add_field(name='MyAnimeList Link',
                                                      value='https://myanimelist.net/manga/' + str(data['idMal']),
                                                      inline=False)
                                manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                       icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=manga_embed)
                                main.logger.info('Server: %s | Response: Random Manga - %s' % (ctx.guild.name,
                                                                                               data['title']['romaji']))
                            except Exception as e:
                                error_embed = discord.Embed(
                                    title='An error occurred while searching for a manga with the genre `%s`' % genre,
                                    color=0xff0000)
                                await ctx.channel.send(embed=error_embed)
                                main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='An manga with the genre `%s` does not exist in the AniList database' % genre,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        else:
            error_embed = discord.Embed(title='Wrong arguments',
                                        color=0xff0000)
            await ctx.channel.send(embed=error_embed)
            main.logger.info('Server: %s | Response: Wrong arguments' % ctx.guild.name)


def setup(client):
    client.add_cog(Random(client))
    main.logger.info('Loaded extension Random')


def teardown():
    main.logger.info('Unloaded extension Random')
