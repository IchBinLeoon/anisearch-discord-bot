import discord
from discord.ext import commands
from discord.ext import menus
from anisearch.utils.formats import description_parser
from anisearch.utils.formats import anilist_type_parsers
from anisearch.utils.formats import anilist_manga_status_parsers
from anisearch.utils.formats import anilist_date_parser
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.queries.manga_query import SEARCH_MANGA_QUERY
from anisearch.utils.requests import anilist_request


class Manga(commands.Cog, name='Manga'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_manga_anilist(self, ctx, title):
        embeds = []
        try:
            variables = {'search': title, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_MANGA_QUERY, variables))['data']['Page']['media']
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the manga `{}`.'
                                  .format(title),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data) > 0:
            pages = len(data)
            current_page = 0
            for manga in data:
                current_page += 1
                try:
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

                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                     'the manga.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='manga', aliases=['m'], usage='manga <title>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_manga(self, ctx, *, title):
        """Searches for a manga with the given title and displays information about the search results such as type, status, chapters, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self._search_manga_anilist(ctx, title)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The manga `{}` could not be found.'.format(title), color=0xff0000)
                await ctx.channel.send(embed=embed)
