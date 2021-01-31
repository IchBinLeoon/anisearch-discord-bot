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
from discord.ext import commands, menus
from discord.ext.commands import Context
from discord.utils import get

from anisearch.bot import AniSearchBot
from anisearch.config import OWNER_ID
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX
from anisearch.utils.miscellaneous import get_invite, get_vote, get_version, get_creator, get_bot, get_url
from anisearch.utils.paginator import EmbedListMenu

log = logging.getLogger(__name__)


class Help(commands.Cog, name='Help'):
    """
    Help cog.
    """

    def __init__(self, bot: AniSearchBot):
        """
        Initializes the `Help` cog.
        """
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name='help', aliases=['h'], usage='help [command]', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx: Context, cmd: Optional[str]):
        """
        Shows help or displays information about a command.
        """
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
                description = command.help.replace('\n', ' ').replace('\r', '')
                embed.add_field(name='Description',
                                value=description, inline=False)
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
        """
        Displays all commands.
        """
        prefix = self.bot.db.get_prefix(ctx)
        if isinstance(ctx.channel, discord.channel.DMChannel):
            server_prefix = ''
        else:
            server_prefix = f'Current server prefix: `{prefix}`\n'

        embeds = []
        page = 1

        for cog in self.bot.cogs:
            cog_ = self.bot.get_cog(cog)
            cmds = cog_.get_commands()
            cmds_ = []
            for cmd in cmds:
                cmd_ = f'• {prefix}{cmd.usage}'
                cmds_.append(cmd_)
            cmds__ = '\n'.join(cmds_)

            if cog_.qualified_name == 'Settings':
                cmds__ = f'Can only be used by a server administrator.\n```\n{cmds__}\n```'
            else:
                cmds__ = f'```\n{cmds__}\n```'

            if cog_.qualified_name != 'Admin':
                embed = discord.Embed(description=f'To view information about a specified command use: '
                                                  f'`{prefix}help [command]`\n'
                                                  f'{server_prefix}'
                                                  f'\n'
                                                  f'**{cog_.qualified_name}**\n'
                                                  f'{cmds__}'
                                                  f'\n'
                                                  f'`<>` - required, `[]` - optional, `|` - either/or',
                                      colour=DEFAULT_EMBED_COLOR)
                embed.set_author(name="AniSearch's commands", icon_url=self.bot.user.avatar_url)
                embed.set_footer(text=f'Commands • Page {page}/{len(self.bot.cogs) - 1}')
                page += 1
                embeds.append(embed)

        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
        await menu.start(ctx)

    @commands.command(name='about', usage='about', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def about(self, ctx: Context):
        """
        Displays information about the bot.
        """
        embed = discord.Embed(title='About AniSearch',
                              description=f'<@!{get_bot()}> is an easy-to-use Discord bot written in Python '
                                          f'that allows you to search for anime, manga, characters, staff, studios and '
                                          f'much more directly in Discord!',
                              color=DEFAULT_EMBED_COLOR)
        embed.add_field(name='❯ Creator', value=f'<@!{get_creator()}>',
                        inline=True)
        embed.add_field(name='❯ Version', value=f'v{get_version()}',
                        inline=True)
        embed.add_field(name='❯ Commands', value=f'{DEFAULT_PREFIX}help',
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
        """
        Displays statistics about the bot.
        """
        embed = discord.Embed(description=f'The current instance of the bot is owned by <@!{OWNER_ID}>',
                              color=DEFAULT_EMBED_COLOR)
        embed.set_author(name="AniSearch's statistics", icon_url=self.bot.user.avatar_url)
        embed.add_field(name='❯ Guilds', value=str(self.bot.get_guild_count()), inline=True)
        embed.add_field(name='❯ Users', value=str(self.bot.get_user_count()), inline=True)
        embed.add_field(name='❯ Channels', value=str(self.bot.get_channel_count()), inline=True)
        embed.add_field(name="❯ AniSearch's Uptime", value=str(self.bot.get_uptime()), inline=True)
        await ctx.channel.send(embed=embed)
