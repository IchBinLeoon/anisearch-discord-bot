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
import platform
from datetime import timedelta, datetime

import discord
import psutil
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
        embed = discord.Embed(title='❯ Bot Status', color=DEFAULT_EMBED_COLOR)
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

    @commands.command(name='sysinfo', aliases=['system', 'sys'], usage='sysinfo', ignore_extra=False, hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def sysinfo(self, ctx: Context):
        """
        Displays basic information about the system on which the bot is currently running. Can only be used by the bot
        owner.
        """
        embed = discord.Embed(title='❯ System Info', color=DEFAULT_EMBED_COLOR)

        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%m/%d/%Y %H:%M:%S")
        embed.add_field(name='Boot Time', value=boot_time, inline=False)

        embed.add_field(name='Platform', value=platform.platform(), inline=False)

        try:
            core_temp = psutil.sensors_temperatures()['cpu_thermal'][0][1]
        except (AttributeError, KeyError):
            core_temp = None
        embed.add_field(name='Temperature', value=f'{core_temp} °C' if core_temp else 'N/A', inline=False)

        embed.add_field(name='Virtual Memory', inline=True,
                        value=f'Total: {round(psutil.virtual_memory()[0] / 1000000000, 2)} GB\n'
                              f'Available: {round(psutil.virtual_memory()[1] / 1000000000, 2)} GB\n'
                              f'Used: {round(psutil.virtual_memory()[3] / 1000000000, 2)} GB\n'
                              f'Usage: {round(psutil.virtual_memory()[2], 2)} %')

        embed.add_field(name='Disk Usage', inline=True,
                        value=f'Total: {round(psutil.disk_usage("/")[0] / 1000000000, 2)} GB\n'
                              f'Available: {round(psutil.disk_usage("/")[2] / 1000000000, 2)} GB\n'
                              f'Used: {round(psutil.disk_usage("/")[1] / 1000000000, 2)} GB\n'
                              f'Usage: {round(psutil.disk_usage("/")[3], 2)} %')

        embed.add_field(name='CPU', inline=True,
                        value=f'Cores: {psutil.cpu_count()}\n'
                              f'Frequency: {round(psutil.cpu_freq(percpu=False)[0], 2)} MHz\n'
                              f'Usage: {round(psutil.cpu_percent(interval=None), 2)} %')

        await ctx.channel.send(embed=embed)
