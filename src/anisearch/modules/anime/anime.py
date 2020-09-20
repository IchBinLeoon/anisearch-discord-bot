import aiohttp
import discord
from discord.ext import commands

import main
from modules.anime import anime_query


class Anime(commands.Cog, name='Anime'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='anime', aliases=['a'], usage='anime <title>', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_anime(self, ctx, *, title):
        """Searches for an anime and shows the first result."""
        api = 'https://graphql.anilist.co'
        query = anime_query.query
        variables = {
            'title': title,
            'page': 1,
            'amount': 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(api, json={'query': query, 'variables': variables}) as r:
                if r.status == 200:
                    json = await r.json()
                    if json['data']['Page']['media']:
                        data = json['data']['Page']['media'][0]
                        try:
                            try:
                                color = int('0x' + data['coverImage']['color'].replace('#', ''), 0)
                            except AttributeError:
                                color = 0x4169E1
                            if data['title']['english'] is None or data['title']['english'] == data['title']['romaji']:
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
                                anime_embed.add_field(name='Start date', value='%s/%s/%s' % (data['startDate']['day'],
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
                                    anime_embed.add_field(name='Duration', value=str(data['duration']) + ' min each',
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
                            anime_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                            if data['synonyms']:
                                anime_embed.add_field(name='Synonyms', value=' | '.join(data['synonyms']), inline=False)
                            else:
                                anime_embed.add_field(name='Synonyms', value='-', inline=True)
                            anime_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                            anime_embed.add_field(name='MyAnimeList Link',
                                                  value='https://myanimelist.net/anime/' + str(data['idMal']),
                                                  inline=False)
                            anime_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=anime_embed)
                            main.logger.info('Server: %s | Response: Anime - %s' % (ctx.guild.name,
                                                                                    data['title']['romaji']))
                        except Exception as e:
                            error_embed = discord.Embed(
                                title='An error occurred while searching for the anime `%s`' % title,
                                color=0xff0000)
                            await ctx.channel.send(embed=error_embed)
                            main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='The anime `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                else:
                    error_embed = discord.Embed(
                        title='An error occurred while searching for the anime `%s`' % title,
                        color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    main.logger.info('Server: %s | Response: Error' % ctx.guild.name)


def setup(client):
    client.add_cog(Anime(client))
    main.logger.info('Loaded extension Anime')


def teardown():
    main.logger.info('Unloaded extension Anime')
