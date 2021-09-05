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

import datetime
import logging
from typing import Dict, Any

import discord
from discord import Embed
from discord.ext import commands, menus
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, ANILIST_LOGO
from anisearch.utils.formatters import format_media_type
from anisearch.utils.menus import EmbedListMenu
from anisearch.utils.types import AniListMediaType

log = logging.getLogger(__name__)


class Schedule(commands.Cog, name='Schedule'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @staticmethod
    async def get_next_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(
                f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(
                    f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
        if data.get('media').get('externalLinks'):
            for i in data.get('media').get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')

        embed = discord.Embed(
            colour=DEFAULT_EMBED_COLOR,
            description=f'Episode **{data.get("episode")}** airing in '
                        f'**{str(datetime.timedelta(seconds=data.get("timeUntilAiring")))}**.\n\n**Type:** '
                        f'{format_media_type(data.get("media")["format"]) if data.get("media")["format"] else "N/A"}'
                        f'\n**Duration:** '
                        f'{str(data.get("media")["duration"]) + " min" if data.get("media")["duration"] else "N/A"}\n'
                        f'\n{" | ".join(sites) if len(sites) > 0 else ""}')

        if data.get('media')['title']['english'] is None or data.get('media')['title']['english'] \
                == data.get('media')['title']['romaji']:
            embed.title = data.get('media')['title']['romaji']
        else:
            embed.title = f'{data.get("media")["title"]["romaji"]} ({data.get("media")["title"]["english"]})'

        embed.set_author(name='Next Airing Episode', icon_url=ANILIST_LOGO)

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_last_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        sites = []
        if data.get('media').get('siteUrl'):
            sites.append(f'[Anilist]({data.get("media").get("siteUrl")})')
        if data.get('media').get('idMal'):
            sites.append(
                f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("media").get("idMal"))})')
        if data.get('media').get('trailer'):
            if data.get('media').get('trailer')['site'] == 'youtube':
                sites.append(
                    f'[Trailer](https://www.youtube.com/watch?v={data.get("media").get("trailer")["id"]})')
        if data.get('media').get('externalLinks'):
            for i in data.get('media').get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')

        date = datetime.datetime.utcfromtimestamp(
            data.get("airingAt")).strftime("%B %d, %Y - %H:%M")

        embed = discord.Embed(
            colour=DEFAULT_EMBED_COLOR,
            description=f'Episode **{data.get("episode")}** aired at **{str(date)}** UTC.\n\n**Type:** '
                        f'{format_media_type(data.get("media")["format"]) if data.get("media")["format"] else "N/A"}'
                        f'\n**Duration:** '
                        f'{str(data.get("media")["duration"]) + " min" if data.get("media")["duration"] else "N/A"}\n'
                        f'\n{" | ".join(sites) if len(sites) > 0 else ""}')

        if data.get('media')['title']['english'] is None or data.get('media')['title']['english'] \
                == data.get('media')['title']['romaji']:
            embed.title = data.get('media')['title']['romaji']
        else:
            embed.title = f'{data.get("media")["title"]["romaji"]} ({data.get("media")["title"]["english"]})'

        embed.set_author(name='Recently Aired Episode', icon_url=ANILIST_LOGO)

        if data.get('media').get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('media')['coverImage']['large'])

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @commands.command(name='next', usage='next', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def next(self, ctx: Context):
        """Displays the next airing anime episodes."""
        async with ctx.channel.typing():
            try:
                data = await self.bot.anilist.schedule(page=1, perPage=15, notYetAired=True, sort='TIME')
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(
                    title=f'An error occurred while searching for the next airing episodes. Try again.',
                    color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, anime in enumerate(data):
                    try:
                        embed = await self.get_next_embed(anime, page + 1, len(data))
                        if not isinstance(ctx.channel, discord.channel.DMChannel):
                            if is_adult(anime.get('media')) and not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the next airing episode.')
                        embed.set_footer(
                            text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The next airing episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='last', usage='last', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def last(self, ctx: Context):
        """Displays the most recently aired anime episodes."""
        async with ctx.channel.typing():
            try:
                data = await self.bot.anilist.schedule(page=1, perPage=15, notYetAired=False, sort='TIME_DESC')
            except Exception as e:
                log.exception(e)
                embed = discord.Embed(
                    title=f'An error occurred while searching for the most recently aired episodes. Try again.',
                    color=ERROR_EMBED_COLOR)
                return await ctx.channel.send(embed=embed)
            if data is not None and len(data) > 0:
                embeds = []
                for page, anime in enumerate(data):
                    try:
                        embed = await self.get_last_embed(anime, page + 1, len(data))
                        if not isinstance(ctx.channel, discord.channel.DMChannel):
                            if is_adult(anime.get('media')) and not ctx.channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    except Exception as e:
                        log.exception(e)
                        embed = discord.Embed(
                            title='Error', color=ERROR_EMBED_COLOR,
                            description=f'An error occurred while loading the embed for the recently aired episode.')
                        embed.set_footer(
                            text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')
                    embeds.append(embed)
                menu = menus.MenuPages(source=EmbedListMenu(
                    embeds), clear_reactions_after=True, timeout=30)
                await menu.start(ctx)
            else:
                embed = discord.Embed(
                    title=f'The most recently aired episodes could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='watchlist', aliases=['wl'], usage='watchlist', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def watchlist(self, ctx: Context):
        """Displays the anime watchlist of the server. If no anime has been added to the watchlist, the server will
        receive a notification for every new episode."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if len(watchlist) > 0:
            data = await self.bot.anilist.watchlist(id_in=watchlist, page=1, perPage=50,
                                                    type=AniListMediaType.Anime.upper())
        else:
            data = None
        if data is not None:
            entries = []
            for i in data:
                entries.append(f'`{i.get("id")}`: [{i.get("title").get("romaji")}]({i.get("siteUrl")})')
            description = '\n'.join(entries)
        else:
            description = '_No anime added to the watchlist. The server will receive a notification for every ' \
                          'new episode._'
        embed = discord.Embed(title='Watchlist', description=description, color=DEFAULT_EMBED_COLOR)
        await ctx.channel.send(embed=embed)

    @commands.command(name='watch', aliases=['w'], usage="watch <AniListID>", ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def watch(self, ctx: Context, anilist_id: int):
        """Adds an anime you want to receive episode notifications from to the server watchlist by
        AniList ID. Can only be used by a server administrator."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if len(watchlist) + 1 > 50:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(
                title=f'The watchlist cannot be longer than 50 entries.',
                color=ERROR_EMBED_COLOR)
            return await ctx.channel.send(embed=embed)
        if anilist_id in watchlist:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(
                title=f'The ID `{anilist_id}` is already on the server watchlist.',
                color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            data = await self.bot.anilist.watchlist(id_in=[anilist_id], page=1, perPage=1,
                                                    type=AniListMediaType.Anime.upper())
            if data is not None:
                self.bot.db.add_watchlist(data[0].get('id'), ctx.guild.id)
                embed = discord.Embed(
                    title=f'Added `{data[0].get("title").get("romaji")}` to the server watchlist.',
                    color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f'An anime with the ID `{anilist_id}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='unwatch', aliases=['uw'], usage="unwatch <AniListID>", ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unwatch(self, ctx: Context, anilist_id: int):
        """Removes an anime from to the server watchlist by AniList ID.
        Can only be used by a server administrator."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if anilist_id not in watchlist:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(
                title=f'The ID `{anilist_id}` is not on the server watchlist.',
                color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            self.bot.db.remove_watchlist(anilist_id, ctx.guild.id)
            embed = discord.Embed(
                title=f'Removed ID `{anilist_id}` from the server watchlist.',
                color=DEFAULT_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    async def send_episode_notification(self, data: Dict[str, Any]) -> None:
        channel_count = 0
        for guild in self.bot.guilds:
            try:
                channel_id = self.bot.db.get_channel(guild)
                if channel_id is not None:
                    channel = guild.get_channel(channel_id)
                    if channel is not None:
                        watchlist = self.bot.db.get_watchlist(guild.id)
                        if len(watchlist) == 0 or data.get('id') in watchlist:

                            if is_adult(data) and not channel.is_nsfw():
                                embed = discord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                      description=f'Adult content. No NSFW channel.')
                                await channel.send(embed=embed)

                            else:

                                embed = discord.Embed(colour=DEFAULT_EMBED_COLOR, url=data.get('url'),
                                                      description=f'Episode **{data.get("episode")}** is out!')

                                embed.set_author(
                                    name='Episode Notification', icon_url=ANILIST_LOGO)

                                if data.get('english') is None or data.get('english') == data.get('romaji'):
                                    embed.title = data.get('romaji')
                                else:
                                    embed.title = f'{data.get("romaji")} ({data.get("english")})'

                                if data.get('image'):
                                    embed.set_image(url=data.get('image'))

                                embed.set_footer(
                                    text=f'Provided by https://anilist.co/')

                                await channel.send(embed=embed)

                            role_id = self.bot.db.get_role(guild)
                            if role_id is not None:
                                await channel.send(f'<@&{role_id}>')

                            channel_count += 1

            except discord.errors.Forbidden as e:
                log.warning(e)

            except Exception as e:
                log.exception(e)

        log.info(f'Posted episode notification in {channel_count} channels')
