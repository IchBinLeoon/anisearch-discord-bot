import discord
import psycopg2
from discord.ext import commands
from typing import Optional

from discord.utils import get

import main
from config import config


def get_prefix(ctx):
    db = psycopg2.connect(host=config.DB_HOST, dbname=config.DB_NAME, user=config.DB_USER, password=config.BD_PASSWORD)
    cur = db.cursor()
    cur.execute('SELECT prefix FROM guilds WHERE id = %s;', (ctx.guild.id,))
    prefix = cur.fetchone()[0]
    db.commit()
    cur.close()
    db.close()
    return prefix


class Help(commands.Cog, name='Help'):

    def __init__(self, client):
        self.client = client
        self.client.remove_command('help')

    @commands.command(name='help', aliases=['h'], usage='help [cmd]', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_help(self, ctx, cmd: Optional[str]):
        """Displays the command list or information about a command."""
        if cmd is None:
            help_embed = discord.Embed(title='%s Commands' % self.client.user.name,
                                       description=f'To view information about a specified command use: `help [cmd]`\n'
                                                   f'Current server prefix: `{get_prefix(ctx)}`\n'
                                                   f'\n'
                                                   f'**Search**\n'
                                                   f'`anime <title>:` Searches for an anime and shows the '
                                                   f'first result.\n '
                                                   f'`manga <title>:` Searches for a manga and shows the '
                                                   f'first result.\n '
                                                   f'`character <name>:` Searches for a character and shows '
                                                   f'the first result.\n '
                                                   f'`staff <name>:` Searches for a staff and shows the first '
                                                   f'result.\n'
                                                   f'`studio <name>:` Searches for a studio and shows the first '
                                                   f'result.\n '
                                                   f'`random <anime | manga> <genre>:` Shows a random anime or manga '
                                                   f'of the specified genre.\n'
                                                   f'\n'
                                                   f'**Profile**\n'
                                                   f'`anilist [username | @user]:` Displays information about a '
                                                   f'AniList Profile.\n'
                                                   f'`myanimelist [username | @user]:` Displays information about a '
                                                   f'MyAnimeList Profile.\n'
                                                   f'`link [anilist/al | myanimelist/mal] [username]:` Links an '
                                                   f'AniList/MyAnimeList Profile.\n'
                                                   f'`removelinks:` Removes the linked AniList and MyAnimeList '
                                                   f'Profile.\n'
                                                   f'\n'
                                                   f'**Info**\n'
                                                   f'`help [cmd]:` Displays the command list or information about '
                                                   f'a command.\n'
                                                   f'`about:` Displays information and stats about the bot.\n'
                                                   f'`contact <message>:` Contacts the creator of the bot.\n'
                                                   f'`ping:` Checks the latency of the bot.\n'
                                                   f'\n'
                                                   f'**Server Administrator**\n'
                                                   f'`prefix <prefix>:` Changes the current server prefix.\n',
                                       color=0x4169E1, timestamp=ctx.message.created_at)
            help_embed.add_field(name='❯ Creator', value='<@!%s>' % main.__owner_id__,
                                 inline=True)
            help_embed.add_field(name='❯ Invite', value='[Click me!](%s)' % main.__invite__,
                                 inline=True)
            help_embed.add_field(name='❯ Vote', value='[Click me!](%s)' % main.__vote__,
                                 inline=True)
            help_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=help_embed)
            main.logger.info('Server: %s | Response: Help' % ctx.guild.name)
        else:
            if command := get(self.client.commands, name=cmd):
                help_embed = discord.Embed(title='Command - %s' % command, colour=0x4169E1)
                help_embed.add_field(name='Usage', value='`%s`' % command.usage,
                                     inline=False)
                help_embed.add_field(name='Description', value='`%s`' % command.help, inline=False)
                help_embed.add_field(name='Cooldown', value='`%s`' % command.brief, inline=False)
                if command.aliases:
                    aliases = ', '.join(command.aliases)
                    help_embed.add_field(name='Aliases', value='`%s`' % aliases, inline=False)
                else:
                    aliases = '-'
                    help_embed.add_field(name='Aliases', value=aliases, inline=False)
                help_embed.set_footer(text='<> - required | [] - optional')
                await ctx.send(embed=help_embed)
                main.logger.info('Server: %s | Response: Help - %s' % (ctx.guild.name, command))
            else:
                error_embed = discord.Embed(title='The command `%s` does not exist' % cmd,
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                main.logger.info('Server: %s | Response: Help command not found' % ctx.guild.name)


def setup(client):
    client.add_cog(Help(client))
    main.logger.info('Loaded extension Help')


def teardown():
    main.logger.info('Unloaded extension Help')
