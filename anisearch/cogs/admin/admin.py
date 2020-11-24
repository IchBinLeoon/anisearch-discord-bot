import math
import platform
import sys
from datetime import datetime, timedelta
from time import time
import discord
import psutil
from discord.ext import commands
from anisearch import config
from anisearch.bot import initial_extensions
from anisearch.utils.logger import logger


class Admin(commands.Cog, name='Admin'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', usage='load <cog>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_load(self, ctx, extension):
        """Loads a cog. // Owner only"""
        try:
            self.bot.load_extension(extension)
            embed = discord.Embed(title='Loaded cog `{}`.'.format(extension),
                                  color=0x4169E1)
            await ctx.channel.send(embed=embed)
            logger.info('Loaded cog {}'.format(extension))
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            embed = discord.Embed(title='Cog `{}` is already loaded.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} is already loaded'.format(extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            embed = discord.Embed(title='Cog `{}` could not be found.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} could not be found'.format(extension))
        except Exception as exception:
            embed = discord.Embed(title='An error occurred while loading the cog `{}`.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.exception(exception)

    @commands.command(name='unload', usage='unload <cog>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_unload(self, ctx, extension):
        """Unloads a cog. // Owner only"""
        try:
            self.bot.unload_extension(extension)
            embed = discord.Embed(title='Unloaded cog `{}`.'.format(extension),
                                  color=0x4169E1)
            await ctx.channel.send(embed=embed)
            logger.info('Unloaded cog {}'.format(extension))
        except discord.ext.commands.errors.ExtensionNotLoaded:
            embed = discord.Embed(title='Cog `{}` has not been loaded.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} has not been loaded'.format(extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            embed = discord.Embed(title='Cog `{}` could not be found.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} could not be found'.format(extension))
        except Exception as exception:
            embed = discord.Embed(title='An error occurred while loading the cog `{}`.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.exception(exception)

    @commands.command(name='reload', usage='reload <cog>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_reload(self, ctx, extension):
        """Reloads a cog. // Owner only"""
        try:
            self.bot.reload_extension(extension)
            embed = discord.Embed(title='Reloaded cog `{}`.'.format(extension),
                                  color=0x4169E1)
            await ctx.channel.send(embed=embed)
            logger.info('Reloaded cog {}'.format(extension))
        except discord.ext.commands.errors.ExtensionNotLoaded:
            embed = discord.Embed(title='Cog `{}` has not been loaded.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} has not been loaded'.format(extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            embed = discord.Embed(title='Cog `{}` could not be found.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.info('Cog {} could not be found'.format(extension))
        except Exception as exception:
            embed = discord.Embed(title='An error occurred while loading the cog `{}`.'.format(extension),
                                  color=0xff0000)
            await ctx.channel.send(embed=embed)
            logger.exception(exception)

    @commands.command(name='shutdown', usage='shutdown', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_shutdown(self, ctx):
        """Shutdowns the bot. // Owner only"""
        embed = discord.Embed(title='Bot is stopping...', color=0x4169E1)
        await ctx.channel.send(embed=embed)
        await self.bot.logout()
        logger.info('Bot is logged out')
        sys.exit(0)

    @commands.command(name='status', usage='status', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_status(self, ctx):
        """Displays the current status of the client. // Owner only"""
        embed = discord.Embed(title='{} - Status'.format(self.bot.user.name),
                              color=0x4169E1)
        embed.add_field(name='Guilds', value=str(len(self.bot.guilds)), inline=True)
        users = 0
        for guild in self.bot.guilds:
            users = users + guild.member_count
        embed.add_field(name='Users', value=users, inline=True)
        channels = 0
        for guild in self.bot.guilds:
            channels = channels + len(guild.channels)
        embed.add_field(name='Channels', value=channels, inline=True)
        proc = psutil.Process()
        with proc.oneshot():
            uptime = timedelta(seconds=round(time() - proc.create_time()))
        try:
            uptime = str(uptime)
        except AttributeError:
            uptime = '-'
        embed.add_field(name="AniSearch's Uptime", value=uptime, inline=True)
        cogs = []
        for i in self.bot.cogs:
            cogs.append(i)
        embed.add_field(name='{}/{} Cogs Loaded'.format(len(self.bot.cogs), len(initial_extensions)),
                        value=', '.join(cogs), inline=False)
        temperature = ''
        try:
            temp = psutil.sensors_temperatures(False)
            if len(temp) > 0:
                core_temp = temp['cpu_thermal']
                temperature = core_temp[0][1]
        except AttributeError:
            temperature = '-'
        system_started = datetime.fromtimestamp(psutil.boot_time()).strftime('%d-%m-%Y %H:%M:%S')
        embed.add_field(name='System',
                        value=f'**OS:** {platform.system()}\n'
                              f'**Temperature:** {temperature}\n'
                              f'**Started:** {system_started}',
                        inline=False)
        embed.add_field(name='CPU',
                        value=f'**Usage:** {psutil.cpu_percent(interval=None)} %\n'
                              f'**Frequency:** {psutil.cpu_freq(percpu=False)[0]} MHz\n'
                              f'**Cores:** {psutil.cpu_count()}\n',
                        inline=True)
        embed.add_field(name='Memory',
                        value=f'**Usage:** {psutil.virtual_memory()[2]} %\n'
                              f'**Used:** {math.ceil(psutil.virtual_memory()[3] // 1000000)} MB\n'
                              f'**Total:** {math.ceil(psutil.virtual_memory()[0] // 1000000)} MB\n',
                        inline=True)
        embed.add_field(name='Disk',
                        value=f'**Usage:** {psutil.disk_usage("/")[3]} %\n'
                              f'**Used:** {math.ceil(psutil.disk_usage("/")[1] // 1000000)} MB\n'
                              f'**Total:** {math.ceil(psutil.disk_usage("/")[0] // 1000000)} MB\n',
                        inline=True)
        await ctx.channel.send(embed=embed)
