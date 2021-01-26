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

import discord
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Theme(commands.Cog, name='Theme'):
    """Theme cog."""

    def __init__(self, bot: AniSearchBot):
        """Initializes the `Theme` cog."""
        self.bot = bot

    @commands.command(name='themes', usage='themes <anime>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def themes(self, ctx: Context, *, anime: str):
        """Searches for the openings and endings of the given anime and displays them."""
        async with ctx.channel.typing():
            data = await self.bot.animethemes.search(anime, 5, ['anime'])
            if data.get('anime'):
                embeds = []
                for page, entry in enumerate(data.get('anime')):
                    try:

                        embed = discord.Embed(color=DEFAULT_EMBED_COLOR, title=entry.get('name'))

                        if entry.get('images'):
                            embed.set_thumbnail(url=entry.get('images')[0]['link'])

                        count = 1
                        sites = []
                        for site in entry.get('resources'):
                            site_string = f'[{site.get("site")}]({site.get("link")})'
                            sites.append(site_string)
                        embed.description = ' | '.join(sites)

                        for theme in entry.get('themes'):
                            if count >= 15:
                                break
                            theme_string = '**Title:** {}{}\n[Link](http://animethemes.moe/video/{})' \
                                .format(theme.get('song')['title'],
                                        ('\n**Artist:** ' + theme.get('song')['artists'][0]['name']) if
                                        theme.get('song')['artists'] else
                                        None, theme.get('entries')[0]['videos'][0]['basename'] if
                                        theme.get('entries')[0]['videos'][0]['basename'] else 'N/A')
                            embed.add_field(
                                name=theme.get('slug').replace('OP', 'Opening ').replace('ED', 'Ending '),
                                value=theme_string, inline=False)
                            count += 1

                        embed.set_footer(
                            text=f'Provided by https://animethemes.moe/ • Page {page + 1}/{len(data.get("anime"))}')

                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error',
                            description=f'An error occurred while loading the embed for the anime.',
                            color=ERROR_EMBED_COLOR)
                        embed.set_footer(
                            text=f'Provided by https://animethemes.moe/ • Page {page + 1}/{len(data.get("anime"))}')
                    embeds.append(embed)

                menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)

            else:
                embed = discord.Embed(title=f'No themes for the anime `{anime}` found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='theme', usage='theme <OP|ED> <anime>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def theme(self, ctx: Context, theme: str, *, anime: str):
        """Displays a specific opening or ending of the given anime."""
        async with ctx.channel.typing():
            data = await self.bot.animethemes.search(anime, 1, ['anime'])
            if data.get('anime'):
                anime_ = data.get('anime')[0]

                for entry in anime_.get('themes'):
                    if theme.upper() == entry.get('slug') or (theme.upper() == 'OP' and entry.get('slug') == 'OP1') or \
                            (theme.upper() == 'ED' and entry.get('slug') == 'ED1'):

                        embed = discord.Embed(title=anime_.get('name'), colour=DEFAULT_EMBED_COLOR)

                        if anime_.get('images'):
                            embed.set_thumbnail(url=anime_.get('images')[0]['link'])

                        info = []
                        sites = []
                        for site in anime_.get('resources'):
                            site_string = f'[{site.get("site")}]({site.get("link")})'
                            sites.append(site_string)
                        sites_joined = ' | '.join(sites) + '\n'
                        info.append(sites_joined)

                        if entry.get('song')['title']:
                            info.append('**Title:** ' + entry.get('song')['title'])

                        if entry.get('song')['artists']:
                            if len(entry.get('song')['artists']) > 1:
                                artists = []
                                for artist in entry.get('song')['artists']:
                                    artists.append(artist.get('name'))
                                info.append('**Artists:** ' + ', '.join(artists))
                            else:
                                info.append('**Artist:** ' + entry.get('song')['artists'][0]['name'])

                        if len(info) > 0:
                            embed.description = '\n'.join(info)

                        embed.set_footer(
                            text=f'Provided by https://animethemes.moe/')

                        await ctx.channel.send(embed=embed)
                        return await ctx.channel.send(
                            f'http://animethemes.moe/video/{entry.get("entries")[0]["videos"][0]["basename"]}')

                embed = discord.Embed(
                    title=f'Cannot find `{theme.upper()}` for the anime `{anime}`.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

            else:
                embed = discord.Embed(title=f'No theme for the anime `{anime}` found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
