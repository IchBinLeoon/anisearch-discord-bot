import datetime
import random
import discord
from discord.ext import commands
from anisearch.utils.formats import anilist_date_parser, anilist_manga_status_parsers
from anisearch.utils.formats import description_parser
from anisearch.utils.formats import anilist_anime_status_parsers
from anisearch.utils.formats import anilist_type_parsers
from anisearch.utils.logger import logger
from anisearch.utils.queries.random_query import SEARCH_RANDOM_ANIME_GENRE_QUERY
from anisearch.utils.queries.random_query import SEARCH_RANDOM_ANIME_TAG_QUERY
from anisearch.utils.queries.random_query import SEARCH_RANDOM_MANGA_GENRE_QUERY
from anisearch.utils.queries.random_query import SEARCH_RANDOM_MANGA_TAG_QUERY
from anisearch.utils.requests import anilist_request


class Random(commands.Cog, name='Random'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_random_anime(self, ctx, genre, query):
        try:
            variables = {'search': genre, 'page': 1, 'amount': 1}
            data = (await anilist_request(query, variables))
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching for an anime with '
                                                             'the genre `{}`. Try again.'.format(genre),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            return embed
        anime = None
        if data['data']['Page']['media'] is not None and len(data['data']['Page']['media']) > 0:
            try:
                page = random.randrange(1, data['data']['Page']['pageInfo']['lastPage'])
                variables = {'search': genre, 'page': page, 'amount': 1}
                anime = (await anilist_request(query, variables))['data']['Page']['media']
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while searching for an anime with '
                                                                 'the genre `{}`.'.format(genre),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                return embed
        if anime is not None and len(anime) > 0:
            try:
                anime = anime[0]
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                if anime['coverImage']['large']:
                    embed.set_thumbnail(url=anime['coverImage']['large'])
                if anime['bannerImage']:
                    embed.set_image(url=anime['bannerImage'])
                anime_stats = []
                if anime['format']:
                    anime_type = 'Type: ' + anilist_type_parsers(anime['format'])
                    anime_stats.append(anime_type)
                if anime['status']:
                    anime_status = 'Status: ' + anilist_anime_status_parsers(anime['status'])
                    anime_stats.append(anime_status)
                if anime['meanScore']:
                    anime_score = 'Score: ' + str(anime['meanScore'])
                    anime_stats.append(anime_score)
                if len(anime_stats) > 0:
                    embed.set_author(name=' | '.join(anime_stats))
                if anime['title']['english'] is None or anime['title']['english'] == anime['title']['romaji']:
                    embed.title = anime['title']['romaji']
                else:
                    embed.title = '{} ({})'.format(anime['title']['romaji'], anime['title']['english'])
                if anime['coverImage']['color']:
                    color = int('0x' + anime['coverImage']['color'].replace('#', ''), 0)
                    embed.color = color
                if anime['description']:
                    description = description_parser(anime['description'], 400)
                    embed.description = description
                try:
                    if anime['status'] == 'RELEASING':
                        try:
                            if anime['nextAiringEpisode']['episode']:
                                anime_episodes = str(anime['nextAiringEpisode']['episode'] - 1)
                                embed.add_field(name='Aired Episodes', value=anime_episodes, inline=True)
                                if anime["nextAiringEpisode"]["timeUntilAiring"]:
                                    seconds = anime["nextAiringEpisode"]["timeUntilAiring"]
                                    time_left = str(datetime.timedelta(seconds=seconds))
                                    embed.add_field(name='Next Episode', value=time_left, inline=True)
                        except TypeError:
                            pass
                    elif anime['episodes']:
                        embed.add_field(name='Episodes', value=anime['episodes'], inline=True)
                except KeyError:
                    pass
                if anime['startDate']['day']:
                    start_date = anilist_date_parser(anime['startDate']['day'], anime['startDate']['month'],
                                                     anime['startDate']['year'])
                    if anime['endDate']['day']:
                        end_date = anilist_date_parser(anime['endDate']['day'], anime['endDate']['month'],
                                                       anime['endDate']['year'])
                    else:
                        end_date = '?'
                    date = '{} to {}'.format(start_date, end_date)
                    embed.add_field(name='Aired', value=date, inline=False)
                if anime['duration']:
                    if anime['episodes'] == 1:
                        anime_duration = str(anime['duration']) + ' min'
                    else:
                        anime_duration = str(anime['duration']) + ' min each'
                    embed.add_field(name='Duration', value=anime_duration, inline=True)
                if anime['source']:
                    embed.add_field(name='Source', value=anime['source'].replace('_', ' ').title(), inline=True)
                try:
                    if anime['studios']['nodes'][0]['name']:
                        embed.add_field(name='Studio', value=anime['studios']['nodes'][0]['name'], inline=True)
                except IndexError:
                    pass
                if anime['synonyms']:
                    embed.add_field(name='Synonyms', value=', '.join(anime['synonyms']), inline=False)
                if anime['genres']:
                    embed.add_field(name='Genres', value=', '.join(anime['genres']), inline=False)
                external_sites = []
                if anime['trailer']:
                    if anime['trailer']['site'] == 'youtube':
                        trailer_site = 'https://www.youtube.com/watch?v=' + anime['trailer']['id']
                        external_sites.append('[Trailer]({})'.format(trailer_site))
                if anime['externalLinks']:
                    for i in anime['externalLinks']:
                        external_sites.append('[{}]({})'.format(i['site'], i['url']))
                if len(external_sites) > 1:
                    embed.add_field(name='Streaming and external sites', value=' | '.join(external_sites),
                                    inline=False)
                sites = []
                if anime['siteUrl']:
                    anilist_link = '[Anilist]({})'.format(anime['siteUrl'])
                    sites.append(anilist_link)
                    embed.url = anime['siteUrl']
                if anime['idMal']:
                    myanimelist_link = '[MyAnimeList](https://myanimelist.net/anime/{})'.format(str(anime['idMal']))
                    sites.append(myanimelist_link)
                if len(sites) > 0:
                    embed.add_field(name='Find out more', value=' | '.join(sites), inline=False)
                embed.set_footer(text='Requested by {}'.format(ctx.author),
                                 icon_url=ctx.author.avatar_url)
                return embed
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while searching for an anime '
                                                                 'with the genre `{}`.'.format(genre),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                return embed

    async def _search_random_manga(self, ctx, genre, query):
        try:
            variables = {'search': genre, 'page': 1, 'amount': 1}
            data = (await anilist_request(query, variables))
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching for a manga with '
                                                             'the genre `{}`. Try again.'.format(genre),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            return embed
        manga = None
        if data['data']['Page']['media'] is not None and len(data['data']['Page']['media']) > 0:
            try:
                page = random.randrange(1, data['data']['Page']['pageInfo']['lastPage'])
                variables = {'search': genre, 'page': page, 'amount': 1}
                manga = (await anilist_request(query, variables))['data']['Page']['media']
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while searching for a manga with '
                                                                 'the genre `{}`.'.format(genre),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                return embed
        if manga is not None and len(manga) > 0:
            try:
                manga = manga[0]
                embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                if manga['coverImage']['large']:
                    embed.set_thumbnail(url=manga['coverImage']['large'])
                if manga['bannerImage']:
                    embed.set_image(url=manga['bannerImage'])
                manga_stats = []
                if manga['format']:
                    manga_type = 'Type: ' + anilist_type_parsers(manga['format'])
                    manga_stats.append(manga_type)
                if manga['status']:
                    manga_status = 'Status: ' + anilist_manga_status_parsers(manga['status'])
                    manga_stats.append(manga_status)
                if manga['meanScore']:
                    manga_score = 'Score: ' + str(manga['meanScore'])
                    manga_stats.append(manga_score)
                if len(manga_stats) > 0:
                    embed.set_author(name=' | '.join(manga_stats))
                if manga['title']['english'] is None or manga['title']['english'] == manga['title']['romaji']:
                    embed.title = manga['title']['romaji']
                else:
                    embed.title = '{} ({})'.format(manga['title']['romaji'], manga['title']['english'])
                if manga['coverImage']['color']:
                    color = int('0x' + manga['coverImage']['color'].replace('#', ''), 0)
                    embed.color = color
                if manga['description']:
                    description = description_parser(manga['description'], 400)
                    embed.description = description
                if manga['chapters']:
                    embed.add_field(name='Chapters', value=manga['chapters'], inline=True)
                if manga['volumes']:
                    embed.add_field(name='Volumes', value=manga['volumes'], inline=True)
                if manga['source']:
                    embed.add_field(name='Source', value=manga['source'].replace('_', ' ').title(), inline=True)
                if manga['startDate']['day']:
                    start_date = anilist_date_parser(manga['startDate']['day'], manga['startDate']['month'],
                                                     manga['startDate']['year'])
                    if manga['endDate']['day']:
                        end_date = anilist_date_parser(manga['endDate']['day'], manga['endDate']['month'],
                                                       manga['endDate']['year'])
                    else:
                        end_date = '?'
                    date = '{} to {}'.format(start_date, end_date)
                    embed.add_field(name='Published', value=date, inline=False)
                if manga['synonyms']:
                    embed.add_field(name='Synonyms', value=', '.join(manga['synonyms']), inline=False)
                if manga['genres']:
                    embed.add_field(name='Genres', value=', '.join(manga['genres']), inline=False)
                if manga['externalLinks']:
                    external_sites = []
                    for i in manga['externalLinks']:
                        external_sites.append('[{}]({})'.format(i['site'], i['url']))
                    if len(external_sites) > 1:
                        embed.add_field(name='External sites', value=' | '.join(external_sites), inline=False)
                sites = []
                if manga['siteUrl']:
                    anilist_link = '[Anilist]({})'.format(manga['siteUrl'])
                    sites.append(anilist_link)
                    embed.url = manga['siteUrl']
                if manga['idMal']:
                    myanimelist_link = '[MyAnimeList](https://myanimelist.net/anime/{})'.format(str(manga['idMal']))
                    sites.append(myanimelist_link)
                if len(sites) > 0:
                    embed.add_field(name='Find out more', value=' | '.join(sites), inline=False)

                embed.set_footer(text='Requested by {}'.format(ctx.author),
                                 icon_url=ctx.author.avatar_url)
                return embed
            except Exception as exception:
                logger.exception(exception)
                embed = discord.Embed(title='Error', description='An error occurred while searching for a manga '
                                                                 'with the genre `{}`.'.format(genre),
                                      color=0xff0000, timestamp=ctx.message.created_at)
                embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
                return embed

    @commands.command(name='random', aliases=['r'], usage='random <anime|manga> <genre>', brief='10s',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cmd_random(self, ctx, media, *, genre):
        """Displays a random anime or manga of the specified genre."""
        async with ctx.channel.typing():
            if media == 'anime' or media == 'Anime':
                embed = await self._search_random_anime(ctx, genre, SEARCH_RANDOM_ANIME_GENRE_QUERY)
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = await self._search_random_anime(ctx, genre, SEARCH_RANDOM_ANIME_TAG_QUERY)
                    if embed:
                        await ctx.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(title='An anime with the genre `{}` could not be found.'.format(genre),
                                              color=0xff0000)
                        await ctx.channel.send(embed=embed)
            elif media == 'manga' or media == 'Manga':
                embed = await self._search_random_manga(ctx, genre, SEARCH_RANDOM_MANGA_GENRE_QUERY)
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = await self._search_random_manga(ctx, genre, SEARCH_RANDOM_MANGA_TAG_QUERY)
                    if embed:
                        await ctx.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(title='A manga with the genre `{}` could not be found.'.format(genre),
                                              color=0xff0000)
                        await ctx.channel.send(embed=embed)
            else:
                ctx.command.reset_cooldown(ctx)
                raise discord.ext.commands.BadArgument
