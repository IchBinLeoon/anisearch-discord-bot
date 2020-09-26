import math
from time import time

import psutil as psutil
import psycopg2

import platform
import sys
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

import logging

from config import config

__version__ = '1.5'
__author__ = 'IchBinLeoon'
__owner_id__ = 223871059068321793
__invite__ = 'https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=83968&scope=bot'
__vote__ = 'https://top.gg/bot/737236600878137363/vote'
__github__ = 'https://github.com/IchBinLeoon/anisearch-discord-bot'

logger = logging.getLogger('anisearch')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

file_handler = logging.FileHandler('anisearch.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

extensions = ['modules.anime.anime', 'modules.manga.manga', 'modules.character.character', 'modules.staff.staff',
              'modules.random.random', 'modules.anilist.anilist', 'modules.studio.studio',
              'modules.myanimelist.myanimelist', 'modules.link.link', 'modules.removelinks.removelinks',
              'modules.prefix.prefix', 'modules.ping.ping', 'modules.help.help', 'modules.about.about',
              'handlers.error_handler', 'events.guild_join', 'events.guild_leave', 'modules.contact.contact',
              'handlers.topgg']


def get_current_time():
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')


def get_command_prefix(client, message):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    try:
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return when_mentioned_or(prefix, 'as!')(client, message)
    except TypeError:
        cur.execute('INSERT INTO guilds (id, prefix) VALUES (%s, %s)', (message.guild.id, 'as!'))
        cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (message.guild.id,))
        prefix = cur.fetchone()[0]
        db.commit()
        cur.close()
        db.close()
        return when_mentioned_or(prefix, 'as!')(client, message)


def get_prefix(ctx):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
    prefix = cur.fetchone()[0]
    db.commit()
    cur.close()
    db.close()
    return prefix


def main():
    client = commands.Bot(command_prefix=get_command_prefix, owner_id=__owner_id__)

    @client.event
    async def on_ready():
        logger.info('Logged in as %s' % client.user)
        logger.info('Client-Name: %s' % client.user.name)
        logger.info('Client-Discriminator: %s' % client.user.discriminator)
        logger.info('Client-ID: %s' % client.user.id)
        logger.info('Client-Version: %s' % __version__)
        logger.info('Discord-Version: %s' % discord.__version__)
        logger.info('Python-Version: %s' % platform.python_version())
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='as!help'),
                                     status=discord.Status.online)
        load_extensions()
        online_embed = discord.Embed(title='Client is online - Extensions loaded %s/%s' % (len(client.cogs),
                                                                                           len(extensions)),
                                     color=0x4169E1)
        await client.get_user(__owner_id__).send(embed=online_embed)

    def load_extensions():
        for i in extensions:
            try:
                client.load_extension(i)
            except Exception as e:
                logger.exception(e)
        logger.info('Extensions loaded %s/%s' % (len(client.cogs), len(extensions)))

    @client.event
    async def on_connect():
        logger.info('Connected to Discord')

    @client.event
    async def on_disconnect():
        logger.info('Disconnected from Discord')

    @client.event
    async def on_command(ctx):
        if ctx.message.author == client.user:
            return
        elif isinstance(ctx.message.channel, discord.channel.DMChannel):
            return
        elif ctx.message.content.startswith('as!'):
            args = ctx.message.content[3:].split(' ')[1:]
            logger.info('Server: %s | Author: %s | Command: %s | Args: %s' % (ctx.guild.name, ctx.author, ctx.command,
                                                                              args))
        elif ctx.message.content.startswith(get_prefix(ctx.message)):
            args = ctx.message.content[len(get_prefix(ctx.message)):].split(' ')[1:]
            logger.info('Server: %s | Author: %s | Command: %s | Args: %s' % (ctx.guild.name, ctx.author, ctx.command,
                                                                              args))

    @client.command(name='load', usage='load <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_load(ctx, extension):
        """Loads an extension. // Creator only"""
        try:
            client.load_extension(extension)
            load_embed = discord.Embed(title='Loaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Loaded extension %s' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while loading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @client.command(name='unload', usage='unload <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_unload(ctx, extension):
        """Unloads an extension. // Creator only"""
        try:
            client.unload_extension(extension)
            load_embed = discord.Embed(title='Unloaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Unloaded extension %s' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while unloading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @client.command(name='reload', usage='reload <extension>', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_reload(ctx, extension):
        """Reloads an extension. // Creator only"""
        client.unload_extension(extension)
        client.load_extension(extension)
        try:
            load_embed = discord.Embed(title='Reloaded extension `%s`' % extension,
                                       color=0x4169E1)
            await ctx.channel.send(embed=load_embed)
            logger.info('Server: %s | Response: Reloaded extension %s' % (ctx.guild.name, extension))
        except Exception as e:
            load_embed = discord.Embed(title='An error occurred while reloading the extension `%s`' % extension,
                                       color=0xff0000)
            await ctx.channel.send(embed=load_embed)
            logger.exception(e)

    @client.command(name='shutdown', usage='shutdown', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_shutdown(ctx):
        """Shutdowns the client. // Creator only"""
        stop_embed = discord.Embed(title='Client is stopping...', color=0x4169E1)
        await ctx.channel.send(embed=stop_embed)
        logger.info('Server: %s | Response: Shutdown' % ctx.guild.name)
        await client.logout()
        logger.info('Client is logged out')
        sys.exit(0)

    @client.command(name='status', usage='status', brief='5s', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def cmd_status(ctx):
        """Displays the current status of the client. // Creator only"""
        status_embed = discord.Embed(title='%s - Status' % client.user.name,
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
        guilds = str(len(client.guilds))
        status_embed.add_field(name='Guilds', value=guilds,
                               inline=True)
        users = str(len(client.users))
        status_embed.add_field(name='Users', value=users,
                               inline=True)
        cog_name = ''
        for i in client.cogs:
            cog_name += f'{i}, '
        status_embed.add_field(name='Loaded Extensions - %s/%s' % (len(client.cogs), len(extensions)), value=cog_name,
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

    client.run(config.TOKEN)


if __name__ == '__main__':
    main()
