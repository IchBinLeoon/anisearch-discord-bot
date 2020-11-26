import discord
from discord.ext import menus
from discord.ext import commands
from animesearch.utils.formats import description_parser
from animesearch.utils.logger import logger
from animesearch.utils.menus import EmbedListMenu
from animesearch.utils.queries.staff_query import SEARCH_STAFF_QUERY
from animesearch.utils.requests import anilist_request


class Staff(commands.Cog, name='Staff'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_staff_anilist(self, ctx, name):
        embeds = []
        try:
            variables = {'search': name, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_STAFF_QUERY, variables))['data']['Page']['staff']
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the staff `{}`. '
                                                             'Try again.'.format(name),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data) > 0:
            pages = len(data)
            current_page = 0
            for staff in data:
                current_page += 1
                try:
                    embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                    if staff['image']['large']:
                        embed.set_thumbnail(url=staff['image']['large'])
                    if staff['name']['native'] is None:
                        embed.title = staff['name']['full']
                    elif staff['name']['full'] is None or staff['name']['full'] == staff['name']['native']:
                        embed.title = staff['name']['native']
                    else:
                        embed.title = '{} ({})'.format(staff['name']['full'], staff['name']['native'])
                    if staff['siteUrl']:
                        embed.url = staff['siteUrl']
                    if staff['description']:
                        embed.description = description_parser(staff['description'], 1000)
                    if staff['staffMedia']['edges']:
                        staff_roles = []
                        for x in staff['staffMedia']['edges']:
                            media_name = '[{}]({})'.format([x][0]['node']['title']['romaji'], [x][0]['node']['siteUrl'])
                            staff_roles.append(media_name)
                        if len(staff_roles) > 5:
                            staff_roles = staff_roles[0:5]
                            staff_roles[4] = staff_roles[4] + '...'
                        embed.add_field(name='Staff Roles', value=' | '.join(staff_roles), inline=False)
                    if staff['characters']['edges']:
                        characters = []
                        for x in staff['characters']['edges']:
                            character_name = '[{}]({})'.format([x][0]['node']['name']['full'],
                                                               [x][0]['node']['siteUrl'])
                            characters.append(character_name)
                        if len(characters) > 5:
                            characters = characters[0:5]
                            characters[4] = characters[4] + '...'
                        embed.add_field(name='Character Roles', value=' | '.join(characters), inline=False)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                     'the staff.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='staff', usage='staff <name>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_staff(self, ctx, *, name):
        """Searches for a staff with the given name and displays information about the search results such as description, staff roles, and character roles!"""
        async with ctx.channel.typing():
            embeds = await self._search_staff_anilist(ctx, name)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The staff `{}` could not be found.'.format(name), color=0xff0000)
                await ctx.channel.send(embed=embed)
