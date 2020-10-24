import discord
import psycopg2
from discord.ext import commands
from typing import Optional

from discord.utils import get

import anisearch
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

    @commands.command(name='help', aliases=['h'], usage='help [command]', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_help(self, ctx, cmd: Optional[str]):
        """Shows help or displays information about a command."""
        prefix = get_prefix(ctx)
        if cmd is None:
            help_embed = discord.Embed(title=self.client.user.name,
                                       description=f'**Current server prefix:** `{prefix}`\n'
                                                   f'\n'
                                                   f'**Command help:**\n'
                                                   f'`{prefix}help [command]`\n'
                                                   f'\n'
                                                   f'**Command list:**\n'
                                                   f'`{prefix}commands`\n'
                                                   f'\n'
                                                   f'**Links:**\n'
                                                   f'[Invite {self.client.user.name}!]({anisearch.__invite__}) | '
                                                   f'[Vote for {self.client.user.name}!]({anisearch.__vote__})',
                                       color=0x4169E1)
            help_embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=help_embed)
            anisearch.logger.info('Server: %s | Response: Help' % ctx.guild.name)
        else:
            if command := get(self.client.commands, name=cmd):
                help_embed = discord.Embed(title='Command - %s' % command, colour=0x4169E1)
                help_embed.add_field(name='Usage', value='`%s%s`' % (prefix, command.usage),
                                     inline=False)
                if command.help.__contains__('|'):
                    help_split = command.help.split('|')
                    description = help_split[0]
                    flags = help_split[1]
                    help_embed.add_field(name='Description', value='%s' % description, inline=False)
                    help_embed.add_field(name='Flags', value='`%s`' % flags, inline=False)
                else:
                    help_embed.add_field(name='Description', value='%s' % command.help, inline=False)
                help_embed.add_field(name='Cooldown', value='`%s`' % command.brief, inline=False)
                if command.aliases:
                    aliases = ', '.join(command.aliases)
                    help_embed.add_field(name='Aliases', value='`%s`' % aliases, inline=False)
                else:
                    aliases = '-'
                    help_embed.add_field(name='Aliases', value=aliases, inline=False)
                help_embed.set_footer(text='<> - required, [] - optional, | - either/or')
                await ctx.send(embed=help_embed)
                anisearch.logger.info('Server: %s | Response: Help - %s' % (ctx.guild.name, command))
            else:
                error_embed = discord.Embed(title='The command `%s` does not exist' % cmd,
                                            color=0xff0000)
                await ctx.channel.send(embed=error_embed)
                anisearch.logger.info('Server: %s | Response: Help command not found' % ctx.guild.name)

    @commands.command(name='commands', aliases=['cmds'], usage='commands', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_commands(self, ctx):
        """Displays all commands."""
        prefix = get_prefix(ctx)
        cmds_embed = discord.Embed(description=f'To view information about a specified command use: '
                                               f'`{prefix}help [command]`\n'
                                               f'Current server prefix: `{prefix}`\n'
                                               f'\n'
                                               f'**Parameters:** `<> - required, [] - optional, | - either/or`\n'
                                               f'\n'
                                               f'Do __not__ include `<>` or `[]` when executing the command.\n'
                                               f'\n'
                                               f'**Search**\n'
                                               f'One of the available command flags for the specified command can be '
                                               f'added at the end for additional or specific information. You can view '
                                               f'the available flags for the command with `{prefix}help [command]` '
                                               f'and all command flags with `{prefix}flags`.\n'
                                               f'```'
                                               f'• {prefix}{self.client.get_command("anime").usage}\n'
                                               f'• {prefix}{self.client.get_command("manga").usage}\n'
                                               f'• {prefix}{self.client.get_command("character").usage}\n'
                                               f'• {prefix}{self.client.get_command("staff").usage}\n'
                                               f'• {prefix}{self.client.get_command("studio").usage}\n'
                                               f'• {prefix}{self.client.get_command("random").usage}\n'
                                               f'```'
                                               f'\n'
                                               f'**Profile**\n'
                                               f'```'
                                               f'• {prefix}{self.client.get_command("anilist").usage}\n'
                                               f'• {prefix}{self.client.get_command("myanimelist").usage}\n'
                                               f'• {prefix}{self.client.get_command("setprofile").usage}\n'
                                               f'• {prefix}{self.client.get_command("remove").usage}\n'
                                               f'```'
                                               f'\n'
                                               f'**Source**\n'
                                               f'```'
                                               f'• {prefix}{self.client.get_command("source").usage}\n'
                                               f'```'
                                               f'\n'
                                               f'**Info**\n'
                                               f'```'
                                               f'• {prefix}{self.client.get_command("help").usage}\n'
                                               f'• {prefix}{self.client.get_command("commands").usage}\n'
                                               f'• {prefix}{self.client.get_command("flags").usage}\n'
                                               f'• {prefix}{self.client.get_command("about").usage}\n'
                                               f'• {prefix}{self.client.get_command("contact").usage}\n'
                                               f'• {prefix}{self.client.get_command("ping").usage}\n'
                                               f'```'
                                               f'\n'
                                               f'**Server Administrator**\n'
                                               f'```'
                                               f'• {prefix}{self.client.get_command("prefix").usage}\n'
                                               f'```',
                                   colour=0x4169E1, timestamp=ctx.message.created_at)
        cmds_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        cmds_embed.set_author(name="%s's commands" % self.client.user.name, icon_url=self.client.user.avatar_url)
        await ctx.send(embed=cmds_embed)
        anisearch.logger.info('Server: %s | Response: Commands' % ctx.guild.name)

    @commands.command(name='flags', usage='flags', brief='3s', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmd_flags(self, ctx):
        """Displays all command flags."""
        prefix = get_prefix(ctx)
        cmds_embed = discord.Embed(description=f'One of these command flags can be added to the end of the `anime, '
                                               f'manga, character, staff or studio` command for additional '
                                               f'information.\n'
                                               f'\n' 
                                               f'You can view the available flags for the command with '
                                               f'`{prefix}help [command]`.\n'
                                               f'\n'
                                               f'**All command flags:**\n'
                                               f'`--search`: Displays all search results.\n'
                                               f'`--characters`: Displays the characters in the media.\n'
                                               f'`--staff`: Displays the staff who produced the media.\n'
                                               f'`--image`: Displays the cover images of the media.\n'
                                               f'`--relations`: Displays other media in the same or connecting '
                                               f'franchise.\n'
                                               f'`--links`: Displays external links to another sites related to the '
                                               f'media.\n'
                                               f'`--streams`: Displays links to legal streaming episodes on external '
                                               f'sites.\n'
                                               f'`--all`: Displays the first search results including all command '
                                               f'flags.',
                                   colour=0x4169E1, timestamp=ctx.message.created_at)
        cmds_embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        cmds_embed.set_author(name="%s's command flags" % self.client.user.name, icon_url=self.client.user.avatar_url)
        await ctx.send(embed=cmds_embed)
        anisearch.logger.info('Server: %s | Response: Command flags' % ctx.guild.name)


def setup(client):
    client.add_cog(Help(client))
    anisearch.logger.info('Loaded extension Help')


def teardown():
    anisearch.logger.info('Unloaded extension Help')
