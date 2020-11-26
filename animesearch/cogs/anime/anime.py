import datetime
import discord
from discord.ext import commands
from discord.ext import menus
from animesearch.utils.formats import description_parser
from animesearch.utils.formats import anilist_type_parsers
from animesearch.utils.formats import anilist_anime_status_parsers
from animesearch.utils.formats import anilist_date_parser
from animesearch.utils.logger import logger
from animesearch.utils.menus import EmbedListMenu
from animesearch.utils.queries.anime_query import SEARCH_ANIME_QUERY
from animesearch.utils.requests import anilist_request


class Anime(commands.Cog, name='Anime'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_anime_anilist(self, ctx, title):
        embeds = []
        try:
            variables = {'search': title, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_ANIME_QUERY, variables))['data']['Page']['media']
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the anime `{}`. '
                                                             'Try again.'.format(title),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data) > 0:
            pages = len(data)
            current_page = 0
            for anime in data:
                current_page += 1
                try:
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
                            if anime['nextAiringEpisode']['episode']:
                                anime_episodes = str(anime['nextAiringEpisode']['episode'] - 1)
                                embed.add_field(name='Aired Episodes', value=anime_episodes, inline=True)
                                if anime["nextAiringEpisode"]["timeUntilAiring"]:
                                    seconds = anime["nextAiringEpisode"]["timeUntilAiring"]
                                    time_left = str(datetime.timedelta(seconds=seconds))
                                    embed.add_field(name='Next Episode', value=time_left, inline=True)
                        elif anime['episodes']:
                            embed.add_field(name='Episodes', value=anime['episodes'], inline=True)
                    except Exception:
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
                    except Exception:
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
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                     'the anime.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='anime', aliases=['a', 'ani'], usage='anime <title>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_anime(self, ctx, *, title):
        """Searches for an anime with the given title and displays information about the search results such as type, status, episodes, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self._search_anime_anilist(ctx, title)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The anime `{}` could not be found.'.format(title), color=0xff0000)
                await ctx.channel.send(embed=embed)
