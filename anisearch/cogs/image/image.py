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
from typing import Optional

import discord
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
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
                if not url.endswith(('.jpg', '.png', '.bmp', '.jpeg')):
                    embed = discord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`).',
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
                                embed = discord.Embed(color=DEFAULT_EMBED_COLOR)

                                if anime.get('title_english') is None or anime.get('title_english') == \
                                        anime.get('title_romaji'):
                                    embed.title = anime.get('title_romaji')
                                else:
                                    embed.title = '{} ({})'.format(anime.get('title_romaji'),
                                                                   anime.get('title_english'))

                                try:
                                    image_url = \
                                        f"https://trace.moe/thumbnail.php?anilist_id={anime.get('anilist_id')}&file=" \
                                        f"{anime.get('filename')}&t={anime.get('at')}&token={anime.get('tokenthumb')}" \
                                            .replace(' ', '%20')
                                    embed.set_image(url=image_url)
                                except Exception as e:
                                    log.exception(e)

                                if anime.get('episode'):
                                    episode = anime.get('episode')
                                    if anime.get('at'):
                                        episode = \
                                            f"{anime.get('episode')} ({str(timedelta(seconds=round(anime.get('at'))))})"
                                    embed.add_field(name='Episode', value=episode, inline=False)
                                if anime.get('synonyms'):
                                    embed.add_field(name='Synonyms', value=', '.join(anime.get('synonyms')),
                                                    inline=False)
                                if anime.get('anilist_id'):
                                    anilist_link = f'https://anilist.co/anime/{str(anime.get("anilist_id"))}'
                                    embed.add_field(name='Anilist Link', value=anilist_link, inline=False)
                                if anime.get('mal_id'):
                                    myanimelist_link = f'https://myanimelist.net/anime/{str(anime.get("mal_id"))}'
                                    embed.add_field(name='MyAnimeList Link', value=myanimelist_link, inline=False)

                                embed.set_footer(
                                    text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data)}')

                                if is_adult(anime):
                                    if not ctx.channel.is_nsfw():
                                        embed = discord.Embed(
                                            title='Error',
                                            color=ERROR_EMBED_COLOR,
                                            description=f'Adult content. No NSFW channel.')
                                        embed.set_footer(
                                            text=f'Provided by https://trace.moe/ • Page {page + 1}/{len(data)}')

                            except Exception as e:
                                log.info(e)

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
                if not url.endswith(('.jpg', '.png', '.bmp', '.jpeg')):
                    embed = discord.Embed(title='No correct url specified (`.jpg`, `.png`, `.bmp`, `.jpeg`).',
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
                                embed = discord.Embed(title='Source', colour=DEFAULT_EMBED_COLOR)

                                if entry.get('header').get('similarity'):
                                    embed.title = f"Source - Similarity: {entry.get('header')['similarity']}%"

                                if entry.get('header').get('thumbnail'):
                                    embed.set_image(url=entry.get('header')['thumbnail'])

                                if entry.get('data').get('material'):
                                    embed.add_field(name='Material', value=entry.get('data')['material'], inline=False)

                                if entry.get('data').get('title'):
                                    embed.add_field(name='Title', value=entry.get('data')['title'], inline=False)

                                if entry.get('data').get('characters'):
                                    embed.add_field(name='Characters', value=entry.get('data')['characters'],
                                                    inline=False)

                                if entry.get('data').get('creator'):
                                    embed.add_field(name='Creator', inline=False,
                                                    value=', '.join(entry.get('data')['creator']) if
                                                    isinstance(entry.get('data')['creator'], list)
                                                    else entry.get('data')['creator'])

                                if entry.get('data').get('author_name'):
                                    embed.add_field(name='Author name', value=entry.get('data')['author_name'],
                                                    inline=False)

                                if entry.get('data').get('author_url'):
                                    embed.add_field(name='Author url', value=entry.get('data')['author_url'],
                                                    inline=False)

                                if entry.get('data').get('eng_name'):
                                    embed.add_field(name='English name', value=entry.get('data')['eng_name'],
                                                    inline=False)

                                if entry.get('data').get('jp_name'):
                                    embed.add_field(name='Japanese name', value=entry.get('data')['jp_name'],
                                                    inline=False)

                                if entry.get('data').get('source'):
                                    embed.add_field(name='Source', value=entry.get('data')['source'], inline=False)

                                if entry.get('data').get('ext_urls'):
                                    embed.add_field(name="URL's", value='\n'.join(entry.get('data')['ext_urls']),
                                                    inline=False)

                                embed.set_footer(
                                    text=f'Provided by https://saucenao.com/ • Page {page + 1}/{len(data)}')

                            except Exception as e:
                                log.info(e)

                                embed = discord.Embed(title='Error', color=DEFAULT_EMBED_COLOR,
                                                      description='An error occurred while loading the embed.')
                                embed.set_footer(
                                    text=f'Provided by https://saucenao.com/ • Page {page + 1}/{len(data)}')

                            embeds.append(embed)

                        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                        await menu.start(ctx)

                    else:
                        embed = discord.Embed(title='No source found.', color=ERROR_EMBED_COLOR)
                        await ctx.channel.send(embed=embed)
