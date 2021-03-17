"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from datetime import timedelta
from typing import Optional, Dict, Any

import discord
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, TRACEMOE_LOGO, SAUCENAO_LOGO
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Image(commands.Cog, name='Image'):
    """
    Image cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Image` cog.
        """
        self.bot = bot

    @staticmethod
    async def get_trace_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `trace` embed.

        Args:
            data (dict): The data about the anime.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(title='Trace', color=DEFAULT_EMBED_COLOR)

        embed.set_author(name=f'Similarity -> {(data.get("similarity")) * 100:0.2f}%', icon_url=TRACEMOE_LOGO)

        if data.get('title_english') is None or data.get('title_english') == \
                data.get('title_romaji'):
            name = data.get('title_romaji')
        else:
            name = '{} ({})'.format(data.get('title_romaji'), data.get('title_english'))
        embed.add_field(name='Anime', value=name, inline=False)

        image_url = f'https://trace.moe/thumbnail.php?anilist_id={data.get("anilist_id")}' \
                    f'&file={data.get("filename")}&t={data.get("at")}' \
                    f'&token={data.get("tokenthumb")}'.replace(' ', '%20')
        embed.set_image(url=image_url)

        embed.add_field(name='Episode', inline=False,
                        value=f'{data.get("episode")} ({str(timedelta(seconds=round(data.get("at"))))})'
                        if data.get("at") else data.get("episode"))

        if data.get('synonyms'):
            embed.add_field(name='Synonyms', inline=False, value=', '.join([f'`{s}`' for s in data.get('synonyms')]))

        embed.add_field(name='Anilist', inline=False,
                        value=f'https://anilist.co/anime/{str(data.get("anilist_id"))}' if
                        data.get('anilist_id') else 'N/A')

        embed.add_field(name='MyAnimeList', inline=False,
                        value=f'https://myanimelist.net/anime/{str(data.get("mal_id"))}' if
                        data.get('mal_id') else 'N/A')

        embed.set_footer(text=f'Provided by https://trace.moe/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_source_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        """
        Returns the `source` embed.

        Args:
            data (dict): The data about the source.
            page (int): The current page.
            pages (page): The number of all pages.

        Returns:
            Embed: A discord embed.
        """
        embed = discord.Embed(title='Source', color=DEFAULT_EMBED_COLOR)

        embed.set_author(name=f'Similarity -> {float(data.get("header").get("similarity")):0.2f}%',
                         icon_url=SAUCENAO_LOGO)

        embed.set_image(url=data.get('header')['thumbnail'])

        if data.get('data').get('material'):
            embed.add_field(name='Material', value=data.get('data')['material'], inline=False)

        if data.get('data').get('title'):
            embed.add_field(name='Title', value=data.get('data')['title'], inline=False)

        if data.get('data').get('characters'):
            embed.add_field(name='Characters', value=data.get('data')['characters'], inline=False)

        if data.get('data').get('creator'):
            embed.add_field(name='Creator', inline=False,
                            value=', '.join(data.get('data')['creator']) if
                            isinstance(data.get('data')['creator'], list)
                            else data.get('data')['creator'])

        if data.get('data').get('author_name'):
            embed.add_field(name='Author Name', value=data.get('data')['author_name'], inline=False)

        if data.get('data').get('author_url'):
            embed.add_field(name='Author Url', value=data.get('data')['author_url'], inline=False)

        if data.get('data').get('eng_name'):
            embed.add_field(name='English Name', value=data.get('data')['eng_name'], inline=False)

        if data.get('data').get('jp_name'):
            embed.add_field(name='Japanese Name', value=data.get('data')['jp_name'], inline=False)

        if data.get('data').get('source'):
            embed.add_field(name='Source', value=data.get('data')['source'], inline=False)

        if data.get('data').get('ext_urls'):
            embed.add_field(name="URL's", value='\n'.join(data.get('data')['ext_urls']), inline=False)

        embed.set_footer(text=f'Provided by https://saucenao.com/ • Page {page}/{pages}')

        return embed

    @commands.command(name='trace', aliases=['t'], usage='trace <image-url|with image as attachment>',
                      ignore_extra=False)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def trace(self, ctx: Context, trace: Optional[str] = None):
        """
        Tries to find the anime the image is from through the image url or the image as attachment.
        """
        async with ctx.channel.typing():
            url = None
            if trace is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = discord.Embed(title='No image to look for the anime.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
            else:
                url = trace
            if url:
                if not url.lower().endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif')):
                    embed = discord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`, `.gif`).',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    try:
                        data = await self.bot.tracemoe.search(url)
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title=f'An error occurred while searching for the anime or the link is invalid.',
                            color=ERROR_EMBED_COLOR)
                        return await ctx.channel.send(embed=embed)
                    if data:
                        embeds = []
                        for page, anime in enumerate(data):
                            try:
                                embed = await self.get_trace_embed(anime, page + 1, len(data))
                                if is_adult(anime):
                                    if not ctx.channel.is_nsfw():
                                        embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                              description=f'Adult content. No NSFW channel.')
                                        embed.set_footer(
                                            text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data)}')
                            except Exception as e:
                                log.exception(e)
                                embed = discord.Embed(title='Error', color=DEFAULT_EMBED_COLOR,
                                                      description='An error occurred while loading the embed.')
                                embed.set_footer(
                                    text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data.get("docs"))}')
                            embeds.append(embed)
                        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                        await menu.start(ctx)
                    else:
                        embed = discord.Embed(title='No anime found.', color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)

    @commands.command(name='source', aliases=['sauce'], usage='source <image-url|with image as attachment>',
                      ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def source(self, ctx: Context, source: Optional[str] = None):
        """
        Tries to find the source of an image through the image url or the image as attachment.
        """
        async with ctx.channel.typing():
            url = None
            if source is None:
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    embed = discord.Embed(title='No image to look for the source.', color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
            else:
                url = source
            if url:
                if not url.lower().endswith(('.jpg', '.png', '.bmp', '.jpeg', '.gif')):
                    embed = discord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`, `.gif`).',
                                          color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                    ctx.command.reset_cooldown(ctx)
                else:
                    try:
                        data = await self.bot.saucenao.search(url)
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
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
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description='An error occurred while loading the embed.')
                                embed.set_footer(
                                    text=f'Provided by https://saucenao.com/ • Page {page + 1}/{len(data)}')
                            embeds.append(embed)
                        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                        await menu.start(ctx)
                    else:
                        embed = discord.Embed(title='No source found.', color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)
