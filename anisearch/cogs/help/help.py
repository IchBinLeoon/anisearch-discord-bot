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
from discord.channel import DMChannel
from discord.ext import commands, menus
from discord.ext.commands import Context
from discord.utils import get

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.config import OWNER_ID
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX, CREATOR_ID, BOT_ID, \
    DISCORD_INVITE, TOPGG_VOTE, ANISEARCH_LOGO
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
        prefix = self.bot.db.get_prefix(ctx.message)
        server_prefix = '' if isinstance(ctx.channel, DMChannel) else f'Current server prefix: `{prefix}`\n'

        if cmd is None:
            embed = discord.Embed(title='AniSearch', color=DEFAULT_EMBED_COLOR,
                                  description=f'{server_prefix}\n**Command help:**\n`{prefix}help [command]`\n\n'
                                              f'**Command list:**\n`{prefix}commands`\n\n**Links:**\n'
                                              f'[Invite AniSearch!]({DISCORD_INVITE}) | '
                                              f'[Vote for AniSearch!]({TOPGG_VOTE})')
            embed.set_thumbnail(url=ANISEARCH_LOGO)
            await ctx.send(embed=embed)

        else:
            if command := get(self.bot.commands, name=cmd.lower()):
                embed = discord.Embed(title=f'Command -> `{command}`', colour=DEFAULT_EMBED_COLOR)
                embed.set_author(name='AniSearch Help', icon_url=ANISEARCH_LOGO)
                embed.add_field(name='Usage', value=f'`{prefix}{command.usage}`', inline=False)
                embed.add_field(name='Description', value=command.help.replace('\n', ' ').replace('\r', ''),
                                inline=False)
                embed.add_field(name='Aliases', inline=False,
                                value=', '.join([f"`{a}`" for a in command.aliases]) if command.aliases else '-')
                embed.set_footer(text=f'<> - required, [] - optional, | - either/or')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f'The command `{cmd}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='commands', aliases=['cmds'], usage='commands', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def commands_(self, ctx: Context):
        """
        Displays all commands.
        """
        prefix = self.bot.db.get_prefix(ctx.message)
        server_prefix = '' if isinstance(ctx.channel, DMChannel) else f'Current server prefix: `{prefix}`\n'
        embeds, page = [], 1

        for cog in self.bot.cogs:
            if self.bot.get_cog(cog).qualified_name not in ['Admin', 'Ipc']:
                cmds = '\n'.join([f'• {prefix}{cmd.usage}' for cmd in self.bot.get_cog(cog).get_commands()])

                cmds = ''.join(f'Can only be used by a server administrator.\n```\n{cmds}\n```'
                               if self.bot.get_cog(cog).qualified_name == 'Settings' else f'```\n{cmds}\n```')

                embed = discord.Embed(description=f'To view information about a specified command use: '
                                                  f'`{prefix}help [command]`\n{server_prefix}\n'
                                                  f'`<>` - required, `[]` - optional, `|` - either/or\n\n'
                                                  f'**{self.bot.get_cog(cog).qualified_name}**\n{cmds}\n'
                                                  f'Do **not** include `<>`, `[]` or `|` when executing the command.',
                                      colour=DEFAULT_EMBED_COLOR)
                embed.set_author(name="AniSearch's commands", icon_url=ANISEARCH_LOGO)
                embed.set_footer(text=f'Commands • Page {page}/{len(self.bot.cogs) - 2}')
                embeds.append(embed)
                page += 1

        menu = menus.MenuPages(source=EmbedListMenu(embeds), clear_reactions_after=True, timeout=30)
        await menu.start(ctx)

    @commands.command(name='about', usage='about', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def about(self, ctx: Context):
        """
        Displays information about the bot.
        """
        embed = discord.Embed(title='About AniSearch', color=DEFAULT_EMBED_COLOR,
                              description=f'<@!{BOT_ID}> is an easy-to-use Discord bot written in Python '
                                          f'that allows you to search for anime, manga, characters, staff, studios '
                                          f'and much more directly in Discord!')
        embed.add_field(name='❯ Creator', value=f'<@!{CREATOR_ID}>', inline=True)
        embed.add_field(name='❯ Version', value=f'v{anisearch.__version__}', inline=True)
        embed.add_field(name='❯ Commands', value=f'{DEFAULT_PREFIX}help', inline=True)
        embed.add_field(name='❯ Invite', value=f'[Click me!]({DISCORD_INVITE})', inline=True)
        embed.add_field(name='❯ Vote', value=f'[Click me!]({TOPGG_VOTE})', inline=True)
        embed.add_field(name='❯ GitHub', value=f'[Click me!]({anisearch.__url__})', inline=True)
        embed.set_thumbnail(url=ANISEARCH_LOGO)
        await ctx.channel.send(embed=embed)

    @commands.command(name='stats', usage='stats', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stats(self, ctx: Context):
        """
        Displays statistics about the bot.
        """
        embed = discord.Embed(description=f'The current instance of the bot is owned by <@!{OWNER_ID}>',
                              color=DEFAULT_EMBED_COLOR)
        embed.set_author(name="AniSearch's statistics", icon_url=ANISEARCH_LOGO)
        embed.add_field(name='❯ Guilds', value=str(self.bot.get_guild_count()), inline=True)
        embed.add_field(name='❯ Users', value=str(self.bot.get_user_count()), inline=True)
        embed.add_field(name='❯ Channels', value=str(self.bot.get_channel_count()), inline=True)
        embed.add_field(name="❯ AniSearch's Uptime", value=str(self.bot.get_uptime()), inline=True)
        await ctx.channel.send(embed=embed)
