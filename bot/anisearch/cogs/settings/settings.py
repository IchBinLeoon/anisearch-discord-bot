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
from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX

log = logging.getLogger(__name__)


class Settings(commands.Cog, name='Settings'):
    """Settings cog."""

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @commands.command(name='setprefix', usage='setprefix <prefix>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx: Context, prefix: str):
        """
        Changes the current server prefix. Max 5 characters. Can only be used by a server administrator.
        """
        if len(prefix) > 5:
            embed = discord.Embed(
                title='The prefix cannot be longer than 5 characters.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        else:
            prefix_old = self.bot.db.get_prefix(ctx.message)
            self.bot.db.update_prefix(ctx.message, prefix)
            prefix_new = self.bot.db.get_prefix(ctx.message)
            if prefix_new == DEFAULT_PREFIX:
                embed = discord.Embed(
                    title=f'{ctx.author} resetted the prefix.', color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title=f'{ctx.author} changed the prefix from `{prefix_old}` to `{prefix_new}`.',
                                      color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='setchannel', aliases=['setc', 'sc'], usage='setchannel [ID]', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setchannel(self, ctx: Context, channel_id: Optional[int]):
        """
        Sets the channel for the anime episode notifications. If no channel ID is specified, the current one is used.
        Can only be used by a server administrator.
        """
        if channel_id is None:
            channel_id = ctx.channel.id
        if ctx.guild.get_channel(channel_id) is None:
            embed = discord.Embed(
                title=f'The channel `{channel_id}` could not be found.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        else:
            self.bot.db.set_channel(channel_id, ctx.guild)
            channel = self.bot.db.get_channel(ctx.guild)
            embed = discord.Embed(title=f'Set the notification channel to:', description=f'<#{channel}>',
                                  color=DEFAULT_EMBED_COLOR)
            await ctx.channel.send(embed=embed)

    @commands.command(name='removechannel', aliases=['rmchannel', 'rmc', 'rc'], usage='removechannel',
                      ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def removechannel(self, ctx):
        """
        Removes the channel set for the anime episode notifications. Can only be used by a server administrator.
        """
        channel = self.bot.db.get_channel(ctx.guild)
        if channel is None:
            embed = discord.Embed(
                title='No notification channel set for the server.', color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        else:
            self.bot.db.set_channel(None, ctx.guild)
            embed = discord.Embed(
                title='Removed the set notification channel.', color=DEFAULT_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
