import logging
from datetime import timedelta
from typing import Optional, Dict, Any

import nextcord
from nextcord import Embed
from nextcord.ext import commands
from nextcord.ext.commands import Context
from pysaucenao import GenericSource

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.menus import EmbedListButtonMenu, SearchButtonMenuPages

log = logging.getLogger(__name__)


class Image(commands.Cog, name='Image'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @staticmethod
    async def get_trace_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = nextcord.Embed(title='Trace', color=DEFAULT_EMBED_COLOR)

        embed.set_author(
            name=f'Similarity » {(data.get("similarity")) * 100:0.2f}%')

        if data.get('anilist').get('title').get('english') is None or \
                data.get('anilist').get('title').get('english') == data.get('anilist').get('title').get('romaji'):
            name = data.get('anilist').get('title').get('romaji')
        else:
            name = '{} ({})'.format(data.get('anilist').get('title').get('romaji'),
                                    data.get('anilist').get('title').get('english'))
        embed.add_field(name='Anime', value=name, inline=False)

        embed.set_image(url=data.get('image'))

        embed.add_field(name='Episode', inline=False,
                        value=f'{data.get("episode")} ({str(timedelta(seconds=round(data.get("from"))))} - '
                              f'{str(timedelta(seconds=round(data.get("to"))))})')

        if data.get('anilist').get('synonyms'):
            embed.add_field(name='Synonyms', inline=False, value=', '.join(
                [f'`{s}`' for s in data.get('anilist').get('synonyms')]))

        embed.add_field(name='Anilist', inline=False,
                        value=f'https://anilist.co/anime/{str(data.get("anilist").get("id"))}' if
                        data.get("anilist").get("id") else 'N/A')

        embed.add_field(name='MyAnimeList', inline=False,
                        value=f'https://myanimelist.net/anime/{str(data.get("anilist").get("idMal"))}' if
                        data.get("anilist").get("idMal") else 'N/A')

        embed.set_footer(
            text=f'Provided by https://trace.moe/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_source_embed(data: GenericSource, page: int, pages: int) -> Embed:
        embed = nextcord.Embed(title='Source', color=DEFAULT_EMBED_COLOR)

        embed.set_author(
            name=f'Similarity » {float(data.similarity):0.2f}%')

        embed.set_image(url=data.thumbnail)

        if data.author_name:
            if data.author_url:
                name = f'[{data.author_name}]({data.author_url})'
            else:
                name = data.author_name
            embed.add_field(name='Author', value=name, inline=False)

        if data.title:
            embed.add_field(name='Title', value=data.title, inline=False)

        if data.urls:
            embed.add_field(name="URL's" if len(data.urls) > 1 else 'URL', value='\n'.join(data.urls), inline=False)

        embed.set_footer(
            text=f'Provided by https://saucenao.com/ • Page {page}/{pages}')

        return embed

    @commands.command(name='trace', usage='trace <image-url|with image as attachment>', ignore_extra=False)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def trace(self, ctx: Context, trace: Optional[str] = None):
        """Tries to find the anime the image is from through the image url or the image as attachment."""
        async with ctx.channel.typing():
            url = None
            if trace is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = nextcord.Embed(
                        title='No image to look for the anime.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
            else:
                url = trace
            if url:
                if not url.lower().endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif')):
                    embed = nextcord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`, `.gif`).',
                                           color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    try:
                        data = await self.bot.tracemoe.search(url, anilist_info=True)
                    except Exception as e:
                        log.exception(e)
                        embed = nextcord.Embed(
                            title=f'An error occurred while searching for the anime, the link is invalid or '
                                  f'the search queue is full.',
                            color=ERROR_EMBED_COLOR)
                        return await ctx.channel.send(embed=embed)
                    if len(data) > 0:
                        embeds = []
                        for page, anime in enumerate(data):
                            try:
                                embed = await self.get_trace_embed(anime, page + 1, len(data))
                                if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                                    if is_adult(anime.get('anilist')) and not ctx.channel.is_nsfw():
                                        embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                               description=f'Adult content. No NSFW channel.')
                                        embed.set_footer(
                                            text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data)}')
                            except Exception as e:
                                log.exception(e)
                                embed = nextcord.Embed(title='Error', color=DEFAULT_EMBED_COLOR,
                                                       description='An error occurred while loading the embed.')
                                embed.set_footer(
                                    text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data)}')
                            embeds.append(embed)
                        menu = SearchButtonMenuPages(
                            source=EmbedListButtonMenu(embeds),
                            clear_buttons_after=True,
                            timeout=60,
                            style=nextcord.ButtonStyle.primary
                        )
                        await menu.start(ctx)
                    else:
                        embed = nextcord.Embed(
                            title='No anime found.', color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)

    @commands.command(name='source', aliases=['sauce'], usage='source <image-url|with image as attachment>',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def source(self, ctx: Context, source: Optional[str] = None):
        """Tries to find the source of an image through the image url or the image as attachment."""
        async with ctx.channel.typing():
            url = None
            if source is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = nextcord.Embed(
                        title='No image to look for the source.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
            else:
                url = source
            if url:
                if not url.lower().endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif')):
                    embed = nextcord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`, `.gif`).',
                                           color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    try:
                        data = await self.bot.saucenao.from_url(url)
                    except Exception as e:
                        log.exception(e)
                        embed = nextcord.Embed(
                            title=f'An error occurred while looking for the source, the link is invalid, or the '
                                  f'daily limit has been reached.',
                            color=ERROR_EMBED_COLOR)
                        return await ctx.channel.send(embed=embed)
                    if data:
                        embeds = []
                        for page, entry in enumerate(data):
                            try:
                                embed = await self.get_source_embed(entry, page + 1, len(data))
                            except Exception as e:
                                log.exception(e)
                                embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                       description='An error occurred while loading the embed.')
                                embed.set_footer(
                                    text=f'Provided by https://saucenao.com/ • Page {page + 1}/{len(data)}')
                            embeds.append(embed)
                        menu = SearchButtonMenuPages(
                            source=EmbedListButtonMenu(embeds),
                            clear_buttons_after=True,
                            timeout=60,
                            style=nextcord.ButtonStyle.primary
                        )
                        await menu.start(ctx)
                    else:
                        embed = nextcord.Embed(
                            title='No source found.', color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)

    @commands.command(name='waifu', usage='waifu', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def waifu(self, ctx: Context):
        """Posts a random image of a waifu."""
        async with ctx.channel.typing():
            data = await self.bot.waifu.sfw('waifu')
            embed = nextcord.Embed(color=DEFAULT_EMBED_COLOR)
            embed.set_image(url=data)
            embed.set_footer(text='Provided by https://waifu.pics/')
            await ctx.channel.send(embed=embed)

    @commands.command(name='neko', aliases=['catgirl', 'meow', 'nya'], usage='neko', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def neko(self, ctx: Context):
        """Posts a random image of a catgirl."""
        async with ctx.channel.typing():
            data = await self.bot.waifu.sfw('neko')
            embed = nextcord.Embed(color=DEFAULT_EMBED_COLOR)
            embed.set_image(url=data)
            embed.set_footer(text='Provided by https://waifu.pics/')
            await ctx.channel.send(embed=embed)


def setup(bot: AniSearchBot):
    bot.add_cog(Image(bot))
    log.info('Image cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Image cog unloaded')
