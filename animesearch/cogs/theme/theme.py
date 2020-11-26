import discord
from discord.ext import commands
from discord.ext import menus
from animesearch.utils.logger import logger
from animesearch.utils.menus import EmbedListMenu
from animesearch.utils.requests import animethemes_request


class Theme(commands.Cog, name='Theme'):

    def __init__(self, bot):
        self.bot = bot

    async def _search_anime_theme(self, ctx, anime):
        embeds = []
        try:
            data = (await animethemes_request(anime))
        except Exception as exception:
            logger.exception(exception)
            embed = discord.Embed(title='Error', description='An error occurred while searching for the themes from the'
                                                             ' anime {}. Try again.'.format(anime),
                                  color=0xff0000, timestamp=ctx.message.created_at)
            embed.set_footer(text='Requested by {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
            embeds.append(embed)
            return embeds
        if data is not None and len(data['anime_list']) > 0:
            pages = len(data['anime_list'])
            current_page = 0
            for anime in data['anime_list']:
                current_page += 1
                try:
                    embed = discord.Embed(color=0x4169E1)
                    if anime['title']:
                        embed.title = anime['title']
                    if anime['cover']:
                        embed.set_thumbnail(url=anime['cover'])
                    x = 0
                    for theme in anime['themes']:
                        if theme['artist']:
                            value = '[{} by {}]({})'.format(theme['title'], theme['artist'],
                                                            theme['mirrors'][0]['mirror'])
                        else:
                            value = '[{}]({})'.format(theme['title'], theme['mirrors'][0]['mirror'])
                        embed.add_field(name=theme['type'], value=value, inline=True)
                        x += 1
                    embed.set_footer(text='Provided by https://animethemes.moe/ • Page {}/{}'.format(current_page,
                                                                                                     pages))
                    embeds.append(embed)
                except Exception as exception:
                    logger.exception(exception)
                    embed = discord.Embed(title='Error', description='An error occurred while loading the embed.',
                                          color=0xff0000, timestamp=ctx.message.created_at)
                    embed.set_footer(text='Requested by {} • Page {}/{}'.format(ctx.author, current_page, pages),
                                     icon_url=ctx.author.avatar_url)
                    embeds.append(embed)
            return embeds

    @commands.command(name='theme', usage='theme <anime>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_theme(self, ctx, *, anime):
        """Searches for themes from the given anime and displays the openings and endings."""
        async with ctx.channel.typing():
            async with ctx.channel.typing():
                embeds = await self._search_anime_theme(ctx, anime)
                if embeds:
                    menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                    await menu.start(ctx)
                else:
                    embed = discord.Embed(title='No theme for the anime `{}` found.'.format(anime), color=0xff0000)
                    await ctx.channel.send(embed=embed)

