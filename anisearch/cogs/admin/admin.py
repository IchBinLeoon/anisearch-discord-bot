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

import discord
from discord.ext import commands
from discord.ext.commands import Context

from anisearch.bot import AniSearchBot, initial_extensions
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR

log = logging.getLogger(__name__)


class Admin(commands.Cog, name='Admin'):
    """
    Admin cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Admin` cog.
        """
        self.bot = bot

    @commands.command(name='status', usage='status', ignore_extra=False, hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def status(self, ctx: Context):
        """
        Displays the current status of the bot. Can only be used by the bot owner.
        """
        embed = discord.Embed(title='AniSearch - Status', color=DEFAULT_EMBED_COLOR)
        embed.add_field(name='Guilds', value=str(self.bot.get_guild_count()), inline=True)
        embed.add_field(name='Users', value=str(self.bot.get_user_count()), inline=True)
        embed.add_field(name='Channels', value=str(self.bot.get_channel_count()), inline=True)
        embed.add_field(name="AniSearch's Uptime", value=str(timedelta(seconds=round(self.bot.get_uptime()))),
                        inline=False)
        embed.add_field(
            name=f'Cogs ({len(self.bot.cogs)}/{len(initial_extensions)})', value=', '.join(self.bot.cogs), inline=False)
        embed.add_field(name='Shards', value=self.bot.shard_count, inline=True)
        embed.add_field(name='Latency', value=str(round(self.bot.latency, 6)), inline=False)
        embed.add_field(
            name='SauceNAO Requests', inline=False,
            value=f'{str(self.bot.saucenao.long_remaining) if self.bot.saucenao.long_remaining else "N/A"} remaining')
        await ctx.channel.send(embed=embed)

    @commands.command(name='load', usage='load <cog>', ignore_extra=False, hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def load(self, ctx: Context, extension: str):
        """
        Loads a cog. Can only be used by the bot owner.
        """
        try:
            self.bot.load_extension(f'anisearch.cogs.{extension.lower()}')
            title = f'Loaded cog `{extension.capitalize()}`.'
            color = DEFAULT_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            title = f'Cog `{extension.capitalize()}` is already loaded.'
            color = ERROR_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionNotFound:
            title = f'Cog `{extension.capitalize()}` could not be found.'
            color = ERROR_EMBED_COLOR
        except Exception as e:
            log.info(e)
            title = f'An error occurred while loading the cog `{extension.capitalize()}`.'
            color = ERROR_EMBED_COLOR
        embed = discord.Embed(title=title, color=color)
        await ctx.channel.send(embed=embed)

    @commands.command(name='unload', usage='unload <cog>', ignore_extra=False, hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def unload(self, ctx: Context, extension: str):
        """
        Unloads a cog. Can only be used by the bot owner.
        """
        try:
            self.bot.unload_extension(f'anisearch.cogs.{extension.lower()}')
            title = f'Unloaded cog `{extension.capitalize()}`.'
            color = DEFAULT_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionNotLoaded:
            title = f'Cog `{extension.capitalize()}` has not been loaded.'
            color = ERROR_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionNotFound:
            title = f'Cog `{extension.capitalize()}` could not be found.'
            color = ERROR_EMBED_COLOR
        except Exception as e:
            log.info(e)
            title = f'An error occurred while unloading the cog `{extension.capitalize()}`.'
            color = ERROR_EMBED_COLOR
        embed = discord.Embed(title=title, color=color)
        await ctx.channel.send(embed=embed)

    @commands.command(name='reload', usage='reload <cog>', brief='5s', ignore_extra=False, hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def reload(self, ctx: Context, extension: str):
        """
        Reloads a cog. Can only be used by the bot owner.
        """
        try:
            self.bot.reload_extension(f'anisearch.cogs.{extension.lower()}')
            title = f'Reloaded cog `{extension.capitalize()}`.'
            color = DEFAULT_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionNotLoaded:
            title = f'Cog `{extension.capitalize()}` has not been loaded.'
            color = ERROR_EMBED_COLOR
        except discord.ext.commands.errors.ExtensionNotFound:
            title = f'Cog `{extension.capitalize()}` could not be found.'
            color = ERROR_EMBED_COLOR
        except Exception as e:
            log.info(e)
            title = f'An error occurred while reloading the cog `{extension.capitalize()}`.'
            color = ERROR_EMBED_COLOR
        embed = discord.Embed(title=title, color=color)
        await ctx.channel.send(embed=embed)
