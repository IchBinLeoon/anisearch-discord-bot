import aiohttp
import discord
from discord.ext import commands

import main
from modules.anime import anime_query


class Anime(commands.Cog, name='Anime'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='anime', aliases=['a'], ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_anime(self, ctx, *, title):
        """Searches for an anime and shows the first result."""
        if title.__contains__('--all'):
            parameters = title.split()
            if parameters.__contains__('--all'):
                parameters.remove('--all')
            separator = ' '
            title = separator.join(parameters)
            api = 'https://graphql.anilist.co'
            query = anime_query.query_pages
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
                            anime_embed = discord.Embed(title='Search results for Anime "%s"' % title,
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
                                anime_embed.add_field(name=str(x + 1) + '. ' + data[x]['title']['romaji'],
                                                      value=value, inline=False)
                                x = x + 1
                            anime_embed.set_thumbnail(url=data[0]['coverImage']['large'])
                            anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anime_embed)
                            main.logger.info('Server: %s | Response: Anime All - %s' % (ctx.guild.name, title))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the anime `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The anime `%s` does not exist in the AniList database' % title,
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
            query = anime_query.query
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
                                anime_embed = discord.Embed(title=data['title']['romaji'], url=data['siteUrl'],
                                                            color=0x4169E1,
                                                            timestamp=ctx.message.created_at)
                            else:
                                anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                               data['title']['english']),
                                                            color=0x4169E1, url=data['siteUrl'],
                                                            timestamp=ctx.message.created_at)
                            anime_embed.set_thumbnail(url=data['coverImage']['large'])
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
                                anime_embed.add_field(name='Characters', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=True)
                            else:
                                anime_embed.add_field(name='Characters', value=characters.__str__()[1:-1]
                                                      .replace("'", "").replace(',', ''), inline=True)
                            anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anime_embed)
                            main.logger.info('Server: %s | Response: Anime Characters - %s' % (ctx.guild.name,
                                                                                               data['title']['romaji']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the anime `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The anime `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
        else:
            api = 'https://graphql.anilist.co'
            query = anime_query.query
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
                                anime_embed = discord.Embed(title=data['title']['romaji'],
                                                            color=0x4169E1, url=data['siteUrl'],
                                                            timestamp=ctx.message.created_at)
                            else:
                                anime_embed = discord.Embed(title='%s (%s)' % (data['title']['romaji'],
                                                                               data['title']['english']),
                                                            color=0x4169E1, url=data['siteUrl'],
                                                            timestamp=ctx.message.created_at)
                            anime_embed.set_thumbnail(url=data['coverImage']['large'])
                            if data['description']:
                                if len(data['description']) < 1024:
                                    anime_embed.add_field(name='Description',
                                                          value=data['description'].replace('<br>', ' ')
                                                          .replace('</br>', ' ')
                                                          .replace('<i>', ' ').replace('</i>', ' '), inline=False)
                                else:
                                    anime_embed.add_field(name='Description',
                                                          value=data['description'].replace('<br>', ' ')
                                                          .replace('</br>', ' ')
                                                          .replace('<i>', ' ').replace('</i>', ' ')[0:1021] + '...',
                                                          inline=False)
                            else:
                                anime_embed.add_field(name='Description',
                                                      value='N/A', inline=False)
                            if data['synonyms']:
                                anime_embed.add_field(name='Synonyms', value=', '.join(data['synonyms']), inline=True)
                            else:
                                anime_embed.add_field(name='Synonyms', value='-', inline=True)
                            anime_embed.add_field(name='Type',
                                                  value=data['format'].replace('_', ' ').title().replace('Tv', 'TV'),
                                                  inline=True)
                            if data['episodes'] is None:
                                anime_embed.add_field(name='Episodes', value='N/A',
                                                      inline=True)
                            else:
                                anime_embed.add_field(name='Episodes', value=data['episodes'],
                                                      inline=True)
                            if data['episodes'] == 1:
                                anime_embed.add_field(name='Duration', value=str(data['duration']) + ' min',
                                                      inline=True)
                            else:
                                anime_embed.add_field(name='Duration', value=str(data['duration']) + ' min each',
                                                      inline=True)
                            anime_embed.add_field(name='Status', value=data['status'].replace('_', ' ').title(),
                                                  inline=True)
                            anime_embed.add_field(name='Start date',
                                                  value='%s/%s/%s' % (data['startDate']['day'],
                                                                      data['startDate']['month'],
                                                                      data['startDate']['year']), inline=True)
                            if data['endDate']['day'] is None:
                                if data['nextAiringEpisode'] is None:
                                    anime_embed.add_field(name='Released episodes', value='N/A',
                                                          inline=True)
                                else:
                                    anime_embed.add_field(name='Released episodes',
                                                          value=data['nextAiringEpisode']['episode'] - 1,
                                                          inline=True)
                            else:
                                anime_embed.add_field(name='End date',
                                                      value='%s/%s/%s' % (data['endDate']['day'],
                                                                          data['endDate']['month'],
                                                                          data['endDate']['year']), inline=True)
                            try:
                                anime_embed.add_field(name='Studio', value=data['studios']['nodes'][0]['name'],
                                                      inline=True)
                            except IndexError:
                                anime_embed.add_field(name='Studio', value='N/A',
                                                      inline=True)
                            anime_embed.add_field(name='Ø Score', value=data['averageScore'], inline=True)
                            anime_embed.add_field(name='Popularity', value=data['popularity'], inline=True)
                            anime_embed.add_field(name='Favourites', value=data['favourites'], inline=True)
                            try:
                                anime_embed.add_field(name='Source', value=data['source'].replace('_', ' ').title(),
                                                      inline=True)
                            except AttributeError:
                                anime_embed.add_field(name='Source', value='N/A',
                                                      inline=True)
                            anime_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                            anime_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                            anime_embed.add_field(name='MyAnimeList Link',
                                                  value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                  inline=False)
                            anime_embed.set_footer(text='Requested by %s' % ctx.author,
                                                   icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anime_embed)
                            main.logger.info('Server: %s | Response: Anime - %s' % (ctx.guild.name,
                                                                                    data['title']['romaji']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the anime `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.error(e)
                    else:
                        error_embed = discord.Embed(
                            title='The anime `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Anime(client))
    main.logger.info('Loaded extension Anime')


def teardown():
    main.logger.info('Unloaded extension Anime')
