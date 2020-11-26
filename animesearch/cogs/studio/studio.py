import discord
from discord.ext import menus
from discord.ext import commands

from animesearch.utils.formats import anilist_type_parsers
from animesearch.utils.logger import logger
from animesearch.utils.menus import EmbedListMenu
from animesearch.utils.queries.studio_query import SEARCH_STUDIO_QUERY
from animesearch.utils.requests import anilist_request


class Studio(commands.Cog, name='Studio'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_studio_anilist(self, ctx, name):
        embeds = []
        try:
            variables = {'search': name, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_STUDIO_QUERY, variables))['data']['Page']['studios']
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the studio `{}`. '
                                                             'Try again.'.format(name),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data) > 0:
            pages = len(data)
            current_page = 0
            for studio in data:
                current_page += 1
                try:
                    embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                    if studio['name']:
                        embed.title = studio['name']
                    if studio['siteUrl']:
                        embed.url = studio['siteUrl']
                    if studio['media']['edges']:
                        medias = []
                        for x in studio['media']['edges']:
                            try:
                                media_name = [x][0]['node']['title']['romaji']
                                media_link = [x][0]['node']['siteUrl']
                                media_type = anilist_type_parsers([x][0]['node']['format'])
                                media_count = [x][0]['node']['episodes']
                                list_object = '[{}]({}) - Type: {} - Episodes: {}'.format(media_name, media_link,
                                                                                          media_type, media_count)
                                medias.append(list_object)
                            except Exception as exception:
                                logger.exception(exception)
                                pass
                        if len(medias) > 10:
                            medias = medias[0:10]
                            medias[9] = medias[9] + '...'
                        embed.add_field(name='Most Popular Productions', value='\n'.join(medias), inline=False)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                     'the studio.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='studio', usage='studio <name>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_studio(self, ctx, *, name):
        """Searches for a studio with the given name and displays information about the search results such as the studio productions!"""
        async with ctx.channel.typing():
            embeds = await self._search_studio_anilist(ctx, name)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The studio `{}` could not be found.'.format(name), color=0xff0000)
                await ctx.channel.send(embed=embed)
