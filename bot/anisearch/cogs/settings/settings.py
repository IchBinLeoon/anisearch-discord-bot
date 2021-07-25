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
import re
from typing import Optional, Union

import discord
from discord.ext import commands
from discord.ext.commands import Context, BadArgument

from anisearch.bot import AniSearchBot
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX

log = logging.getLogger(__name__)


class Settings(commands.Cog, name='Settings'):
    """Settings cog."""

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    @commands.command(name='set', usage='set <prefix|channel|role> <prefix|#channel|@role>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set(self, ctx: Context, type_: str, value: str):
        """Sets the server prefix, the channel for anime episode notifications, or the role for notification mentions.
        Can only be used by a server administrator."""
        if type_.lower() == 'prefix':
            if len(value) > 5:
                embed = discord.Embed(
                    title='The prefix cannot be longer than 5 characters.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
                ctx.command.reset_cooldown(ctx)
            else:
                prefix_old = self.bot.db.get_prefix(ctx.message)
                self.bot.db.update_prefix(ctx.message, value)
                prefix_new = self.bot.db.get_prefix(ctx.message)
                if prefix_new == DEFAULT_PREFIX:
                    embed = discord.Embed(
                        title=f'{ctx.author} reset the prefix.', color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f'{ctx.author} changed the prefix from `{prefix_old}` to `{prefix_new}`.',
                        color=DEFAULT_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
        elif type_.lower() == 'channel':
            if value.startswith('<#'):
                channel_id = value.replace('<#', '').replace('>', '')
            else:
                channel_id = value
            try:
                channel_id = int(channel_id)
            except ValueError:
                channel_id = None
            if ctx.guild.get_channel(channel_id) is None:
                embed = discord.Embed(
                    title=f'The channel could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
                ctx.command.reset_cooldown(ctx)
            else:
                self.bot.db.set_channel(channel_id, ctx.guild)
                channel = self.bot.db.get_channel(ctx.guild)
                embed = discord.Embed(title=f'Set the notification channel to:', description=f'<#{channel}>',
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
                embed = discord.Embed(
                    title=f'The role could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
                ctx.command.reset_cooldown(ctx)
            else:
                self.bot.db.set_role(role_id, ctx.guild)
                role = self.bot.db.get_role(ctx.guild)
                embed = discord.Embed(title=f'Set the notification role to:', description=f'<@&{role}>',
                                      color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            raise discord.ext.commands.BadArgument

    @commands.command(name='remove', aliases=['rm'], usage='remove <channel|role>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx: Context, type_: str):
        """
        Removes the set channel or role. Can only be used by a server administrator.
        """
        if type_.lower() == 'channel':
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
        elif type_.lower() == 'role':
            role = self.bot.db.get_role(ctx.guild)
            if role is None:
                embed = discord.Embed(
                    title='No notification role set for the server.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
            else:
                self.bot.db.set_role(None, ctx.guild)
                embed = discord.Embed(
                    title='Removed the set notification role.', color=DEFAULT_EMBED_COLOR)
                await ctx.channel.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            raise discord.ext.commands.BadArgument

    @commands.command(name='info', usage='info', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def info(self, ctx: Context):
        """
        Displays the set prefix, the set channel and the set role. Can only be used by a server administrator.
        """
        prefix = self.bot.db.get_prefix(ctx.message)
        channel = self.bot.db.get_channel(ctx.guild)
        role = self.bot.db.get_role(ctx.guild)
        embed = discord.Embed(title=ctx.guild.name, color=DEFAULT_EMBED_COLOR)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name='Prefix', value=prefix, inline=False)
        embed.add_field(
            name='Channel', value=f'<#{channel}>' if channel else '*Not set*', inline=False)
        embed.add_field(
            name='Role', value=f'<@&{role}>' if role else '*Not set*', inline=False)
        await ctx.channel.send(embed=embed)

