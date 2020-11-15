import discord
from discord.ext import menus
from discord.ext import commands
from anisearch.utils.embeds import anilist_not_found_error_embed
from anisearch.utils.embeds import anilist_load_embed_error_embed
from anisearch.utils.embeds import anilist_request_error_embed
from anisearch.utils.logger import logger
from anisearch.utils.queries.studio_query import SEARCH_STUDIO_QUERY
from anisearch.utils.requests import anilist_request


async def _search_studio_anilist(ctx, name):
    embeds = []
    try:
        variables = {'search': name, 'page': 1, 'amount': 15}
        data = (await anilist_request(SEARCH_STUDIO_QUERY, variables))['data']['Page']['studios']
    except Exception as exception:
        logger.exception(exception)
        embed = anilist_request_error_embed(ctx, 'studio', name, exception)
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
                    media = []
                    for x in studio['media']['edges']:
                        media_name = '[{}]({})'.format([x][0]['node']['title']['romaji'], [x][0]['node']['siteUrl'])
                        media.append(media_name)
                    if len(media) > 10:
                        media = media[0:10]
                        media[9] = media[9] + '...'
                    embed.add_field(name='Productions', value=' | '.join(media), inline=False)
                embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                 icon_url=ctx.author.avatar_url)
                embeds.append(embed)
            except Exception as exception:
                logger.exception(exception)
                embed = anilist_load_embed_error_embed(ctx, 'studio', exception, current_page, pages)
                embeds.append(embed)
        return embeds


class Studio(commands.Cog, name='Studio'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='studio', usage='studio [name]', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def studio(self, ctx, *, name):
        """Searches for a studio with the given name and displays information about the first result such as the studio productions!"""
        async with ctx.channel.typing():
            embeds = await _search_studio_anilist(ctx, name)
            if embeds:
                menu = menus.MenuPages(source=StudioMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = anilist_not_found_error_embed(ctx, 'studio', name)
                await ctx.channel.send(embed=embed)


class StudioMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, embeds):
        return embeds
