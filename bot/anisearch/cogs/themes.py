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
from typing import Dict, Any
from urllib.parse import urljoin

import nextcord
from nextcord import Embed
from nextcord.ext import commands, menus
from nextcord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, ANIMETHEMES_BASE_URL
from anisearch.utils.http import get
from anisearch.utils.menus import EmbedListButtonMenu

log = logging.getLogger(__name__)


class Themes(commands.Cog, name='Themes'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @staticmethod
    async def get_themes_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = nextcord.Embed(color=DEFAULT_EMBED_COLOR,
                               title=data.get('name'))

        embed.set_author(name='Themes')

        if data.get('images'):
            embed.set_thumbnail(url=data.get('images')[0]['link'])

        if data.get('resources'):
            embed.description = ' | '.join([f'[{site.get("site")}]({site.get("link")})' for site in
                                            data.get('resources')])

        count = 1
        for theme in data.get('animethemes'):
            if count >= 15:
                embed.add_field(name=theme.get('slug'),
                                value='...', inline=False)
                break
            count += 1

            list_ = ['**Title:** ' + theme.get('song')['title']]

            if theme.get('song')['artists']:
                list_.append('**Artist:** ' + theme.get('song')['artists'][0]['name'])

            link = f'[Link](https://animethemes.moe/video/' \
                   f'{theme.get("animethemeentries")[0]["videos"][0]["basename"]})'
            list_.append(link)

            embed.add_field(name=theme.get('slug'),
                            value='\n'.join(list_), inline=False)

        embed.set_footer(
            text=f'Provided by https://animethemes.moe/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_theme_embed(anime: Dict[str, Any], data: Dict[str, Any]) -> Embed:
        embed = nextcord.Embed(color=DEFAULT_EMBED_COLOR,
                               title=anime.get("name"))

        embed.set_author(name=data.get('slug').replace(
            'OP', 'Opening ').replace('ED', 'Ending '))

        if anime.get('images'):
            embed.set_thumbnail(url=anime.get("images")[0]["link"])

        list_ = []

        if anime.get('resources'):
            list_.append(' | '.join([f'[{site.get("site")}]({site.get("link")})' for site in
                                     anime.get('resources')]) + '\n')

        list_.append('**Title:** ' + data.get('song')['title'])

        if data.get('song')['artists']:
            list_.append('**Artist:** ' + data.get('song')['artists'][0]['name'] if
                         len(data.get('song')['artists']) == 1 else
                         '**Artists:** ' + ', '.join([a.get("name") for a in data.get('song')['artists']]))

        embed.description = '\n'.join(list_) if len(list_) > 0 else 'N/A'

        embed.set_footer(text=f'Provided by https://animethemes.moe/')

        return embed

    @commands.command(name='themes', usage='themes <anime>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def themes(self, ctx: Context, *, anime: str):
        """Searches for the openings and endings of the given anime and displays them."""
        async with ctx.channel.typing():
            params = {
                'q': anime,
                'limit': 15,
                'fields[search]': 'anime',
                'include[anime]': 'animethemes.animethemeentries.videos,animethemes.song.artists,images'
            }
            data = await get(url=urljoin(ANIMETHEMES_BASE_URL, 'search'), session=self.bot.session,
                             res_method='json', params=params, headers={'User-Agent': 'AniSearch Discord Bot'})
            if data.get('search').get('anime'):
                embeds = []
                for page, entry in enumerate(data.get('search').get('anime')):
                    try:
                        embed = await self.get_themes_embed(entry, page + 1, len(data.get('search').get('anime')))
                        if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                            if is_adult(entry.get('animethemes')[0]['animethemeentries'][0]) and not \
                                    ctx.channel.is_nsfw():
                                embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                       description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://animethemes.moe/ • Page {page + 1}/'
                                         f'{len(data.get("search").get("anime"))}')
                    except Exception as e:
                        log.exception(e)
                        embed = nextcord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the anime.')
                        embed.set_footer(
                            text=f'Provided by https://animethemes.moe/ • Page '
                                 f'{page + 1}/{len(data.get("search").get("anime"))}')
                    embeds.append(embed)
                menu = menus.ButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'No themes for the anime `{anime}` found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='theme', usage='theme <OP|ED> <anime>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def theme(self, ctx: Context, theme: str, *, anime: str):
        """Displays a specific opening or ending of the given anime."""
        async with ctx.channel.typing():
            params = {
                'q': anime,
                'limit': 1,
                'fields[search]': 'anime',
                'include[anime]': 'animethemes.animethemeentries.videos,animethemes.song.artists,images'
            }
            data = await get(url=urljoin(ANIMETHEMES_BASE_URL, 'search'), session=self.bot.session,
                             res_method='json', params=params, headers={'User-Agent': 'AniSearch Discord Bot'})
            if data.get('search').get('anime'):
                anime_ = data.get('search').get('anime')[0]
                for entry in anime_.get('animethemes'):
                    if theme.upper() == entry.get('slug') or \
                            (theme.upper() == 'OP' and entry.get('slug') == 'OP1') or \
                            (theme.upper() == 'ED' and entry.get('slug') == 'ED1') or \
                            (theme.upper() == 'OP1' and entry.get('slug') == 'OP') or \
                            (theme.upper() == 'ED1' and entry.get('slug') == 'ED'):
                        try:
                            embed = await self.get_theme_embed(anime_, entry)
                            if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                                if is_adult(entry.get('animethemeentries')[0]) and not ctx.channel.is_nsfw():
                                    embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                           description=f'Adult content. No NSFW channel.')
                                    embed.set_footer(
                                        text=f'Provided by https://animethemes.moe/')
                                    return await ctx.channel.send(embed=embed)
                        except Exception as e:
                            log.exception(e)
                            embed = nextcord.Embed(
                                title='Error', color=ERROR_EMBED_COLOR,
                                description=f'An error occurred while loading the embed for the theme.')
                            embed.set_footer(
                                text=f'Provided by https://animethemes.moe/')
                        await ctx.channel.send(embed=embed)
                        return await ctx.channel.send(
                            f'https://animethemes.moe/video/'
                            f'{entry.get("animethemeentries")[0]["videos"][0]["basename"]}')
                embed = nextcord.Embed(
                    title=f'Cannot find `{theme.upper()}` for the anime `{anime}`.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    title=f'No theme for the anime `{anime}` found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)


def setup(bot: AniSearchBot):
    bot.add_cog(Themes(bot))
    log.info('Themes cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Themes cog unloaded')
