import aiohttp
import discord
from discord.ext import commands

import main
from modules.manga import manga_query


class Manga(commands.Cog, name='Manga'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='manga', aliases=['m'], ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_manga(self, ctx, *, title):
        """Searches for a manga and shows the first result."""
        if title.__contains__('--all'):
            parameters = title.split()
            if parameters.__contains__('--all'):
                parameters.remove('--all')
            separator = ' '
            title = separator.join(parameters)
            api = 'https://graphql.anilist.co'
            query = manga_query.query_pages
            variables = {
                'title': title,
                'page': 1,
                'amount': 10,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        if json['data']['Page']['media']:
                            data = json['data']['Page']['media']
                        try:
                            manga_embed = discord.Embed(title='Search results for Manga "%s"' % title,
                                                        color=0x4169E1, timestamp=ctx.message.created_at)
                            x = 0
                            for i in data:
                                if data[x]['title']['english'] is None or data[x]['title']['english'] == \
                                        data[x]['title']['romaji']:
                                    value = '[' + str(data[x]['title']['romaji']) + '](' + str(data[x]['siteUrl']) + \
                                            ')'
                                else:
                                    value = '[' + str(data[x]['title']['english']) + '](' + str(data[x]['siteUrl']) + \
                                            ')'
                                manga_embed.add_field(name=str(x + 1) + '. ' + data[x]['title']['romaji'],
                                                      value=value, inline=False)
                                x = x + 1
                            manga_embed.set_thumbnail(url=data[0]['coverImage']['large'])
                            manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=manga_embed)
                            main.logger.info('Server: %s | Response: Manga All - %s' % (ctx.guild.name, title))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the manga `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The manga `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        elif title.__contains__('--chars') or title.__contains__('--characters'):
            parameters = title.split()
            if parameters.__contains__('--chars'):
                parameters.remove('--chars')
            elif parameters.__contains__('--characters'):
                parameters.remove('--characters')
            separator = ' '
            title = separator.join(parameters)
            api = 'https://graphql.anilist.co'
            query = manga_query.query
            variables = {
                'title': title
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        data = json['data']['Media']
                        try:
                            if data['title']['english'] is None or data['title']['english'] == data['title']['romaji']:
                                manga_embed = discord.Embed(title=data['title']['romaji'], url=data['siteUrl'],
                                                            color=0x4169E1,
                                                            timestamp=ctx.message.created_at)
                            else:
                                manga_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                               data['title']['english']),
                                                            color=0x4169E1, url=data['siteUrl'],
                                                            timestamp=ctx.message.created_at)
                            manga_embed.set_thumbnail(url=data['coverImage']['large'])
                            if data['characters']['edges']:
                                characters = []
                                x = 0
                                characters_length = int(len(data['characters']['edges']))
                                for i in range(0, characters_length - 1):
                                    characters.append(
                                        str('[' + data['characters']['edges'][x]['node']['name']['full'] + ']('
                                            + data['characters']['edges'][x]['node']['siteUrl'] + ') |'))
                                    x = x + 1
                                characters.append(str('[' + data['characters']['edges'][x]['node']['name']['full']
                                                      + '](' + data['characters']['edges'][x]['node']['siteUrl'] + ')'))
                            else:
                                characters = '[N/A]'
                            if len(str(characters)) > 1024:
                                characters = characters[0:15]
                                characters[14] = str(characters[14]).replace(' |', '...')
                                manga_embed.add_field(name='Characters', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=True)
                            else:
                                manga_embed.add_field(name='Characters', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=True)
                            manga_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=manga_embed)
                            main.logger.info('Server: %s | Response: Manga Characters - %s' % (ctx.guild.name,
                                                                                               data['title']['romaji']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the manga `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The manga `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        else:
            api = 'https://graphql.anilist.co'
            query = manga_query.query
            variables = {
                'title': title
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json={'query': query, 'variables': variables}) as r:
                    if r.status == 200:
                        json = await r.json()
                        data = json['data']['Media']
                        try:
                            if data['title']['english'] is None or data['title']['english'] == data['title']['romaji']:
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
                                manga_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']), inline=True)
                            else:
                                manga_embed.add_field(name='Synonyms', value='-', inline=True)
                            manga_embed.add_field(name='Type',
                                                  value=data['format'].replace('_', ' ').title().replace('Tv', 'TV'),
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
                            main.logger.info('Server: %s | Response: Manga - %s' % (ctx.guild.name,
                                                                                    data['title']['romaji']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the manga `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The manga `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Manga(client))
    main.logger.info('Loaded extension Manga')


def teardown():
    main.logger.info('Unloaded extension Manga')
