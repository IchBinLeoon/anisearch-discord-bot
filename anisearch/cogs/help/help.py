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
from discord.utils import get

from anisearch.bot import AniSearchBot
from anisearch.config import OWNER_ID
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR
from anisearch.utils.miscellaneous import get_guild_count, get_user_count, get_channel_count, get_uptime, get_invite, \
    get_vote, get_version, get_creator, get_bot, get_url

log = logging.getLogger(__name__)


class Help(commands.Cog, name='Help'):
    """Help cog."""

    def __init__(self, bot: AniSearchBot):
        """Initializes the `Help` cog."""
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name='help', aliases=['h'], usage='help [command]', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx: Context, cmd: Optional[str]):
        """Shows help or displays information about a command."""
        prefix = self.bot.db.get_prefix(ctx)
        if isinstance(ctx.channel, discord.channel.DMChannel):
            server_prefix = ''
        else:
            server_prefix = f'Current server prefix: `{prefix}`\n'
        if cmd is None:
            embed = discord.Embed(title='AniSearch',
                                  description=f'{server_prefix}'
                                              f'\n'
                                              f'**Command help:**\n'
                                              f'`{prefix}help [command]`\n'
                                              f'\n'
                                              f'**Command list:**\n'
                                              f'`{prefix}commands`\n'
                                              f'\n'
                                              f'**Links:**\n'
                                              f'[Invite AniSearch!]({get_invite()}) | '
                                              f'[Vote for AniSearch!]({get_vote()})',
                                  color=DEFAULT_EMBED_COLOR)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
        else:
            if command := get(self.bot.commands, name=cmd):
                embed = discord.Embed(
                    title=f'Command - {command}', colour=DEFAULT_EMBED_COLOR)
                embed.add_field(name='Usage', value=f'`{prefix}{command.usage}`',
                                inline=False)
                embed.add_field(name='Description',
                                value=f'{command.help}', inline=False)
                if command.aliases:
                    aliases = ', '.join(command.aliases)
                    embed.add_field(
                        name='Aliases', value=f'{aliases}', inline=False)
                else:
                    aliases = '-'
                    embed.add_field(
                        name='Aliases', value=aliases, inline=False)
                embed.set_footer(
                    text='<> - required, [] - optional, | - either/or')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f'The command `{cmd}` does not exist.',
                                      color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='commands', aliases=['cmds'], usage='commands', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def commands_(self, ctx: Context):
        """Displays all commands."""
        prefix = self.bot.db.get_prefix(ctx)
        if isinstance(ctx.channel, discord.channel.DMChannel):
            server_prefix = ''
        else:
            server_prefix = f'Current server prefix: `{prefix}`\n'
        embed = discord.Embed(description=f'To view information about a specified command use: '
                                          f'`{prefix}help [command]`\n'
                                          f'{server_prefix}'
                                          f'\n'
                                          f'**Parameters:** `<> - required, [] - optional, | - either/or`\n'
                                          f'\n'
                                          f'Do __not__ include `<>`, `[]` or `|` when executing the command.\n'
                                          f'\n'
                                          f'**Search**\n'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("anime").usage}\n'
                                          f'• {prefix}{self.bot.get_command("manga").usage}\n'
                                          f'• {prefix}{self.bot.get_command("character").usage}\n'
                                          f'• {prefix}{self.bot.get_command("staff").usage}\n'
                                          f'• {prefix}{self.bot.get_command("studio").usage}\n'
                                          f'• {prefix}{self.bot.get_command("random").usage}\n'
                                          f'• {prefix}{self.bot.get_command("themes").usage}\n'
                                          f'• {prefix}{self.bot.get_command("theme").usage}\n'
                                          f'• {prefix}{self.bot.get_command("trace").usage}\n'
                                          f'```'
                                          f'\n'
                                          f'**Help**\n'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("help").usage}\n'
                                          f'• {prefix}{self.bot.get_command("commands").usage}\n'
                                          f'• {prefix}{self.bot.get_command("about").usage}\n'
                                          f'• {prefix}{self.bot.get_command("stats").usage}\n'
                                          f'```'
                                          f'\n'
                                          f'**Settings**\n'
                                          f'Can only be used by a server administrator.'
                                          f'```'
                                          f'• {prefix}{self.bot.get_command("prefix").usage}\n'
                                          f'```',
                              colour=DEFAULT_EMBED_COLOR)
        embed.set_author(name="AniSearch's commands",
                         icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='about', usage='about', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def about(self, ctx: Context):
        """Displays information about the bot."""
        embed = discord.Embed(title='About AniSearch',
                              description=f'<@!{get_bot()}> is an easy-to-use Discord bot written in Python '
                                          f'that allows you to search for anime, manga, characters, staff, studios and '
                                          f'much more directly in Discord!',
                              color=DEFAULT_EMBED_COLOR)
        embed.add_field(name='❯ Creator', value=f'<@!{get_creator()}>',
                        inline=True)
        embed.add_field(name='❯ Version', value=f'v{get_version()}',
                        inline=True)
        embed.add_field(name='❯ Commands', value='as!help',
                        inline=True)
        embed.add_field(name='❯ Invite', value=f'[Click me!]({get_invite()})',
                        inline=True)
        embed.add_field(name='❯ Vote', value=f'[Click me!]({get_vote()})',
                        inline=True)
        embed.add_field(name='❯ GitHub', value=f'[Click me!]({get_url()})',
                        inline=True)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(name='stats', usage='stats', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stats(self, ctx: Context):
        """Displays statistics about the bot."""
        embed = discord.Embed(description=f'The current instance of the Bot is owned by <@!{OWNER_ID}>',
                              color=DEFAULT_EMBED_COLOR)
        embed.set_author(name="AniSearch's statistics",
                         icon_url=self.bot.user.avatar_url)
        embed.add_field(name='❯ Guilds', value=str(get_guild_count(self.bot)), inline=True)
        embed.add_field(name='❯ Users', value=str(get_user_count(self.bot)), inline=True)
        embed.add_field(name='❯ Channels', value=str(get_channel_count(self.bot)), inline=True)
        embed.add_field(name="❯ AniSearch's Uptime", value=str(get_uptime(self.bot)), inline=True)
        await ctx.channel.send(embed=embed)
