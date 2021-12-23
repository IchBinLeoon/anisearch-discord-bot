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

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, ANILIST_LOGO
from anisearch.utils.types import AniListMediaType

log = logging.getLogger(__name__)


class Notification(commands.Cog, name='Notification'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @commands.command(name='watchlist', aliases=['wl'], usage='watchlist', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def watchlist(self, ctx: Context):
        """Displays the anime watchlist of the server. If no anime has been added to the watchlist, the server will
        receive a notification for every new episode, provided the channel has been set."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        channel = self.bot.db.get_channel(ctx.guild)
        role = self.bot.db.get_role(ctx.guild)
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
                          'new episode, provided the channel has been set._'
        embed = nextcord.Embed(title='Watchlist', description=description, color=DEFAULT_EMBED_COLOR)
        embed.add_field(name='Channel', value=f'<#{channel}>' if channel else '*Not set*', inline=False)
        embed.add_field(name='Role', value=f'<@&{role}>' if role else '*Not set*', inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command(name='watch', aliases=['w'], usage='watch <anilist-id>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def watch(self, ctx: Context, anilist_id: int):
        """Adds an anime you want to receive episode notifications from to the server watchlist by
        AniList ID. Can only be used by a server administrator."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if len(watchlist) + 1 > 50:
            ctx.command.reset_cooldown(ctx)
            embed = nextcord.Embed(
                title=f'The watchlist cannot be longer than 50 entries.',
                color=ERROR_EMBED_COLOR)
            return await ctx.channel.send(embed=embed)
        if anilist_id in watchlist:
            ctx.command.reset_cooldown(ctx)
            embed = nextcord.Embed(
                title=f'The ID `{anilist_id}` is already on the server watchlist.',
                color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            data = await self.bot.anilist.watchlist(id_in=[anilist_id], page=1, perPage=1,
                                                    type=AniListMediaType.Anime.upper())
            if data is not None:
                self.bot.db.add_watchlist(data[0].get('id'), ctx.guild.id)
                embed = nextcord.Embed(
                    title=f'Added `{data[0].get("title").get("romaji")}` to the server watchlist.',
                    color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    title=f'An anime with the ID `{anilist_id}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='unwatch', aliases=['uw'], usage='unwatch <anilist-id>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unwatch(self, ctx: Context, anilist_id: int):
        """Removes an anime from the server watchlist by AniList ID. Can only be used by a server administrator."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if anilist_id not in watchlist:
            ctx.command.reset_cooldown(ctx)
            embed = nextcord.Embed(
                title=f'The ID `{anilist_id}` is not on the server watchlist.',
                color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            self.bot.db.remove_watchlist(anilist_id, ctx.guild.id)
            embed = nextcord.Embed(
                title=f'Removed ID `{anilist_id}` from the server watchlist.',
                color=DEFAULT_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    @commands.command(name='clearlist', aliases=['cl'], usage='clearlist', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def clearlist(self, ctx: Context):
        """Removes all anime from the server watchlist. Can only be used by a server administrator."""
        watchlist = self.bot.db.get_watchlist(ctx.guild.id)
        if len(watchlist) < 1:
            ctx.command.reset_cooldown(ctx)
            embed = nextcord.Embed(
                title='No anime added to the watchlist.',
                color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            self.bot.db.clear_watchlist(ctx.guild.id)
            embed = nextcord.Embed(
                title='Removed all anime from the server watchlist.',
                color=DEFAULT_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    @commands.command(name='set', usage='set <channel|role> <#channel|@role>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set(self, ctx: Context, type_: str, value: str):
        """Sets the channel for anime episode notifications, or the role for notification mentions.
        Can only be used by a server administrator."""
        if type_.lower() == 'channel':
            if value.startswith('<#'):
                channel_id = value.replace('<#', '').replace('>', '')
            else:
                channel_id = value
            try:
                channel_id = int(channel_id)
            except ValueError:
                channel_id = None
            if ctx.guild.get_channel(channel_id) is None:
                embed = nextcord.Embed(
                    title=f'The channel could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
                ctx.command.reset_cooldown(ctx)
            else:
                self.bot.db.set_channel(channel_id, ctx.guild)
                channel = self.bot.db.get_channel(ctx.guild)
                embed = nextcord.Embed(title=f'Set the notification channel to:', description=f'<#{channel}>',
                                       color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        elif type_.lower() == 'role':
            if value.startswith('<@&'):
                role_id = value.replace('<@&', '').replace('>', '')
            else:
                role_id = value
            try:
                role_id = int(role_id)
            except ValueError:
                role_id = None
            if ctx.guild.get_role(role_id) is None:
                embed = nextcord.Embed(
                    title=f'The role could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
                ctx.command.reset_cooldown(ctx)
            else:
                self.bot.db.set_role(role_id, ctx.guild)
                role = self.bot.db.get_role(ctx.guild)
                embed = nextcord.Embed(title=f'Set the notification role to:', description=f'<@&{role}>',
                                       color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            raise nextcord.ext.commands.BadArgument

    @commands.command(name='remove', aliases=['rm'], usage='remove <channel|role>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx: Context, type_: str):
        """Removes the set channel or role. Can only be used by a server administrator."""
        if type_.lower() == 'channel':
            channel = self.bot.db.get_channel(ctx.guild)
            if channel is None:
                embed = nextcord.Embed(
                    title='No notification channel set for the server.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                self.bot.db.set_channel(None, ctx.guild)
                embed = nextcord.Embed(
                    title='Removed the set notification channel.', color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        elif type_.lower() == 'role':
            role = self.bot.db.get_role(ctx.guild)
            if role is None:
                embed = nextcord.Embed(
                    title='No notification role set for the server.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                self.bot.db.set_role(None, ctx.guild)
                embed = nextcord.Embed(
                    title='Removed the set notification role.', color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            raise nextcord.ext.commands.BadArgument

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
                                embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                       description=f'Adult content. No NSFW channel.')
                                await channel.send(embed=embed)

                            else:

                                embed = nextcord.Embed(colour=DEFAULT_EMBED_COLOR, url=data.get('url'),
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

            except nextcord.errors.Forbidden as e:
                log.warning(e)

            except Exception as e:
                log.exception(e)

        log.info(f'Posted episode notification in {channel_count} channels')


def setup(bot: AniSearchBot):
    bot.add_cog(Notification(bot))
    log.info('Notification cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Notification cog unloaded')
