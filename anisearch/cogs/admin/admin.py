import math
import platform
import sys
from datetime import datetime, timedelta
from time import time
import discord
import psutil
from discord.ext import commands

from anisearch import config
from anisearch.bot import logger, initial_extensions


class Admin(commands.Cog, name='Admin'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='load', usage='load <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_load(self, ctx, extension):
        """Loads an extension. // Creator only"""
        try:
            self.client.load_extension(extension)
            load_embed = discord.Embed(title='Loaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Loaded extension %s' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            load_embed = discord.Embed(title='Extension `%s` is already loaded.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s is already loaded' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            load_embed = discord.Embed(title='Extension %s could not be found.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s could not be found' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while loading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @commands.command(name='unload', usage='unload <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_unload(self, ctx, extension):
        """Unloads an extension. // Creator only"""
        try:
            self.client.unload_extension(extension)
            load_embed = discord.Embed(title='Unloaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Unloaded extension %s' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionNotLoaded:
            load_embed = discord.Embed(title='Extension `%s` has not been loaded.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s has not been loaded' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            load_embed = discord.Embed(title='Extension %s could not be found.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s could not be found' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while unloading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @commands.command(name='reload', usage='reload <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_reload(self, ctx, extension):
        """Reloads an extension. // Creator only"""
        try:
            self.client.unload_extension(extension)
            self.client.load_extension(extension)
            load_embed = discord.Embed(title='Reloaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Reloaded extension %s' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionNotLoaded:
            load_embed = discord.Embed(title='Extension `%s` has not been loaded.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s has not been loaded' % (ctx.guild.name, extension))
        except discord.ext.commands.errors.ExtensionNotFound:
            load_embed = discord.Embed(title='Extension %s could not be found.' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Extension %s could not be found' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while reloading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @commands.command(name='shutdown', usage='shutdown', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_shutdown(self, ctx):
        """Shutdowns the client. // Creator only"""
        stop_embed = discord.Embed(title='Client is stopping...', color=0x4169E1)
        await ctx.channel.send(embed=stop_embed)
        logger.info('Server: %s | Response: Shutdown' % ctx.guild.name)
        await self.client.logout()
        logger.info('Client is logged out')
        sys.exit(0)

    @commands.command(name='status', usage='status', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_status(self, ctx):
        """Displays the current status of the client. // Creator only"""
        status_embed = discord.Embed(title='%s - Status' % self.client.user.name,
                                     color=0x4169E1)
        proc = psutil.Process()
        with proc.oneshot():
            uptime = timedelta(seconds=round(time() - proc.create_time()))
        try:
            status_embed.add_field(name='Uptime', value=str(uptime), inline=True)
        except AttributeError:
            status_embed.add_field(name='Uptime', value='-',
                                   inline=True)
        status_embed.add_field(name='Database', value=config.DB_NAME,
                               inline=True)
        guilds = str(len(self.client.guilds))
        status_embed.add_field(name='Guilds', value=guilds,
                               inline=True)
        users = 0
        for guild in self.client.guilds:
            users = users + guild.member_count
        status_embed.add_field(name='Users', value=users,
                               inline=True)
        cog_name = ''
        for i in self.client.cogs:
            cog_name += f'{i}, '
        status_embed.add_field(name='Loaded Extensions - %s/%s' % (len(self.client.cogs), len(initial_extensions)),
                               value=cog_name,
                               inline=False)
        temperature = ''
        try:
            temp = psutil.sensors_temperatures(False)
            if len(temp) > 0:
                core_temp = temp['cpu_thermal']
                temperature = core_temp[0][1]
        except AttributeError:
            temperature = '-'
        system_started = datetime.fromtimestamp(psutil.boot_time()).strftime('%d-%m-%Y %H:%M:%S')
        status_embed.add_field(name='System',
                               value=f'**OS:** {platform.system()}\n'
                                     f'**Temperature:** {temperature}\n'
                                     f'**Started:** {system_started}',
                               inline=False)
        status_embed.add_field(name='CPU',
                               value=f'**Usage:** {psutil.cpu_percent(interval=None)} %\n'
                                     f'**Frequency:** {psutil.cpu_freq(percpu=False)[0]} MHz\n'
                                     f'**Cores:** {psutil.cpu_count()}\n',
                               inline=True)
        status_embed.add_field(name='Memory',
                               value=f'**Usage:** {psutil.virtual_memory()[2]} %\n'
                                     f'**Used:** {math.ceil(psutil.virtual_memory()[3] // 1000000)} MB\n'
                                     f'**Total:** {math.ceil(psutil.virtual_memory()[0] // 1000000)} MB\n',
                               inline=True)
        status_embed.add_field(name='Disk',
                               value=f'**Usage:** {psutil.disk_usage("/")[3]} %\n'
                                     f'**Used:** {math.ceil(psutil.disk_usage("/")[1] // 1000000)} MB\n'
                                     f'**Total:** {math.ceil(psutil.disk_usage("/")[0] // 1000000)} MB\n',
                               inline=True)
        await ctx.channel.send(embed=status_embed)
        logger.info('Server: %s | Response: Status' % ctx.guild.name)
