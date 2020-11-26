import discord
from discord.ext import menus
from discord.ext import commands
from anisearch.utils.formats import description_parser
from anisearch.utils.logger import logger
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.queries.character_query import SEARCH_CHARACTER_QUERY
from anisearch.utils.requests import anilist_request


class Character(commands.Cog, name='Character'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_character_anilist(self, ctx, name):
        embeds = []
        try:
            variables = {'search': name, 'page': 1, 'amount': 15}
            data = (await anilist_request(SEARCH_CHARACTER_QUERY, variables))['data']['Page']['characters']
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching the character `{}`. '
                                                             'Try again.'.format(name),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data) > 0:
            pages = len(data)
            current_page = 0
            for character in data:
                current_page += 1
                try:
                    embed = discord.Embed(timestamp=ctx.message.created_at, color=0x4169E1)
                    if character['image']['large']:
                        embed.set_thumbnail(url=character['image']['large'])
                    if character['name']['full'] is None or character['name']['full'] == character['name']['native']:
                        embed.title = character['name']['native']
                    else:
                        embed.title = '{} ({})'.format(character['name']['full'], character['name']['native'])
                    if character['siteUrl']:
                        embed.url = character['siteUrl']
                    if character['description']:
                        description = description_parser(character['description'], 1000)
                        embed.description = description
                    if character['name']['alternative'] != ['']:
                        embed.add_field(name='Synonyms', value=', '.join(character['name']['alternative']),
                                        inline=False)
                    if character['media']['edges']:
                        media = []
                        for x in character['media']['edges']:
                            media_name = '[{}]({})'.format([x][0]['node']['title']['romaji'], [x][0]['node']['siteUrl'])
                            media.append(media_name)
                        if len(media) > 5:
                            media = media[0:5]
                            media[4] = media[4] + '...'
                        embed.add_field(name='Appearances', value=' | '.join(media), inline=False)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed for '
                                                                     'the character.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='character', aliases=['c', 'char'], usage='character <name>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_character(self, ctx, *, name):
        """Searches for a character with the given name and displays information about the search results such as description, synonyms, and appearances!"""
        async with ctx.channel.typing():
            embeds = await self._search_character_anilist(ctx, name)
            if embeds:
                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(title='The character `{}` could not be found.'.format(name), color=0xff0000)
                await ctx.channel.send(embed=embed)
