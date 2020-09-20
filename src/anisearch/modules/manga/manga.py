import aiohttp
import discord
from discord.ext import commands

import main
from modules.manga import manga_query


class Manga(commands.Cog, name='Manga'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='manga', aliases=['m'], usage='manga <title>', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_manga(self, ctx, *, title):
        """Searches for a manga and shows the first result."""
        api = 'https://graphql.anilist.co'
        query = manga_query.query
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
                                    manga_embed.add_field(name='Chapters', value='%s (%s Volumes)' % (data['chapters'],
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
                            manga_embed.add_field(name='Genres', value=', '.join(data['genres']), inline=False)
                            if data['synonyms']:
                                manga_embed.add_field(name='Synonyms', value=' | '.join(data['synonyms']),
                                                      inline=False)
                            else:
                                manga_embed.add_field(name='Synonyms', value='-', inline=True)
                            manga_embed.add_field(name='AniList Link', value=data['siteUrl'], inline=False)
                            manga_embed.add_field(name='MyAnimeList Link',
                                                  value='https://myanimelist.net/anime/' + str(data['idMal']),
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
                            main.logger.exception(e)
                    else:
                        error_embed = discord.Embed(
                            title='The manga `%s` does not exist in the AniList database' % title,
                            color=0xff0000)
                        await ctx.channel.send(embed=error_embed)
                        main.logger.info('Server: %s | Response: Not found' % ctx.guild.name)
                else:
                    error_embed = discord.Embed(
                        title='An error occurred while searching for the manga `%s`' % title,
                        color=0xff0000)
                    await ctx.channel.send(embed=error_embed)
                    main.logger.info('Server: %s | Response: Error' % ctx.guild.name)


def setup(client):
    client.add_cog(Manga(client))
    main.logger.info('Loaded extension Manga')


def teardown():
    main.logger.info('Unloaded extension Manga')
