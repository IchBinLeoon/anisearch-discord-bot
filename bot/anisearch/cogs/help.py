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
from typing import Optional

import nextcord
from nextcord.channel import DMChannel
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.utils import get, find

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.config import BOT_OWNER_ID
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX, CREATOR_ID, BOT_ID, \
    DISCORD_INVITE, WEBSITE, GITHUB_REPO_API_ENDPOINT, SUPPORT_SERVER_INVITE
from anisearch.utils.http import get as get_request
from anisearch.utils.menus import EmbedListButtonMenu, SearchButtonMenuPages
from anisearch.utils.misc import get_command_example

log = logging.getLogger(__name__)


class Help(commands.Cog, name='Help'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name='help', usage='help [command]', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx: Context, cmd: Optional[str]):
        """Shows help or displays information about a command."""
        prefix = self.bot.db.get_prefix(ctx.message)
        server_prefix = '' if isinstance(
            ctx.channel, DMChannel) else f'Current server prefix: `{prefix}`\n'

        if cmd is None:
            embed = nextcord.Embed(title='AniSearch', color=DEFAULT_EMBED_COLOR,
                                   description=f'{server_prefix}\n**Command help:**\n`{prefix}help [command]`\n\n'
                                               f'**Command list:**\n`{prefix}commands`\n\n**Links:**\n'
                                               f'[Invite AniSearch!]({DISCORD_INVITE}) | '
                                               f'[Support Server]({SUPPORT_SERVER_INVITE}) | '
                                               f'[Website]({WEBSITE})')
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        else:
            if command := get(self.bot.commands, name=cmd.lower()) or \
                          find(lambda cmd_: cmd.lower() in cmd_.aliases, self.bot.commands):
                embed = nextcord.Embed(
                    title=f'Command » `{command}`', colour=DEFAULT_EMBED_COLOR)
                embed.set_author(name='AniSearch Help',
                                 icon_url=self.bot.user.display_avatar.url)
                embed.add_field(
                    name='Usage', value=f'`{prefix}{command.usage}`', inline=False)
                embed.add_field(name='Description', value=command.help.replace('\n', ' ').replace('\r', ''),
                                inline=False)
                if command.aliases:
                    embed.add_field(name='Aliases', inline=False,
                                    value=', '.join([f"`{a}`" for a in command.aliases]) if command.aliases else '-')
                if example := get_command_example(ctx=ctx, command=str(command)):
                    embed.add_field(
                        name='Example', value=f'`{prefix}{example}`', inline=False)
                embed.set_footer(
                    text=f'<> - required, [] - optional, | - either/or')
                await ctx.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    title=f'The command `{cmd}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='commands', aliases=['cmds'], usage='commands', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def commands_(self, ctx: Context):
        """Displays all commands."""
        prefix = self.bot.db.get_prefix(ctx.message)
        server_prefix = '' if isinstance(
            ctx.channel, DMChannel) else f'Current server prefix: `{prefix}`\n'
        embeds, page = [], 1

        for cog in self.bot.cogs:
            if self.bot.get_cog(cog).qualified_name not in ['Admin']:
                cmds = '\n'.join(
                    [f'• {prefix}{cmd.usage}' for cmd in self.bot.get_cog(cog).get_commands()])

                cmds = ''.join(f'```\n{cmds}\n```')

                embed = nextcord.Embed(description=f'To view information about a specified command use: '
                                                   f'`{prefix}help [command]`\n{server_prefix}\n'
                                                   f'`<>` - required, `[]` - optional, `|` - either/or\n\n'
                                                   f'**{self.bot.get_cog(cog).qualified_name}**\n{cmds}\n'
                                                   f'Do **not** include `<>`, `[]` or `|` when executing the command.',
                                       colour=DEFAULT_EMBED_COLOR)
                embed.set_author(name="AniSearch's commands",
                                 icon_url=self.bot.user.display_avatar.url)
                embed.set_footer(
                    text=f'Commands • Page {page}/{len(self.bot.cogs) - 1}')
                embeds.append(embed)
                page += 1

        menu = SearchButtonMenuPages(
            source=EmbedListButtonMenu(embeds),
            clear_buttons_after=True,
            timeout=60,
            style=nextcord.ButtonStyle.primary
        )
        await menu.start(ctx)

    @commands.command(name='about', usage='about', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def about(self, ctx: Context):
        """Displays information about the bot."""
        embed = nextcord.Embed(title='About AniSearch', color=DEFAULT_EMBED_COLOR,
                               description=f'<@!{BOT_ID}> is an easy-to-use bot that allows you to look up information '
                                           f'about anime, manga and much more directly in Discord!')
        embed.add_field(name='❯ Creator',
                        value=f'<@!{CREATOR_ID}>', inline=True)
        embed.add_field(name='❯ Version',
                        value=f'v{anisearch.__version__}', inline=True)
        embed.add_field(name='❯ Commands',
                        value=f'{DEFAULT_PREFIX}help', inline=True)
        embed.add_field(name='❯ Invite',
                        value=f'[Click me!]({DISCORD_INVITE})', inline=True)
        embed.add_field(name='❯ Support Server',
                        value=f'[Click me!]({SUPPORT_SERVER_INVITE})', inline=True)
        embed.add_field(name='❯ Website',
                        value=f'[Click me!]({WEBSITE})', inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.channel.send(embed=embed)

    @commands.command(name='stats', usage='stats', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stats(self, ctx: Context):
        """Displays statistics about the bot."""
        embed = nextcord.Embed(description=f'The current instance of the bot is owned by <@!{BOT_OWNER_ID}>',
                               color=DEFAULT_EMBED_COLOR)
        embed.set_author(name="AniSearch's statistics",
                         icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name='❯ Guilds', value=str(
            self.bot.get_guild_count()), inline=True)
        embed.add_field(name='❯ Users', value=str(
            self.bot.get_user_count()), inline=True)
        embed.add_field(name='❯ Channels', value=str(
            self.bot.get_channel_count()), inline=True)
        embed.add_field(name='❯ Uptime', value=str(
            timedelta(seconds=round(self.bot.get_uptime()))), inline=True)
        embed.add_field(name='❯ Shards',
                        value=self.bot.shard_count, inline=True)
        embed.add_field(name='❯ Latency', value=str(
            round(self.bot.latency, 5)), inline=True)
        await ctx.channel.send(embed=embed)

    @commands.command(name='github', aliases=['gh'], usage='github', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def github(self, ctx: Context):
        """Displays information about the GitHub repository."""
        data = None
        try:
            data = await get_request(url=GITHUB_REPO_API_ENDPOINT, session=self.bot.session, res_method='json')
        except Exception as e:
            log.exception(e)
            embed = nextcord.Embed(title='An error occurred while retrieving data from the GitHub repository.',
                                   color=ERROR_EMBED_COLOR)
            await ctx.channel.send(embed=embed)
        if data:
            embed = nextcord.Embed(title=data.get('full_name'), url=data.get('html_url'),
                                   description=data.get('description'), color=DEFAULT_EMBED_COLOR)
            embed.set_author(name='GitHub Repository')
            embed.add_field(name='❯ Stargazers', value=data.get(
                'stargazers_count'), inline=True)
            embed.add_field(name='❯ Forks', value=data.get(
                'forks_count'), inline=True)
            embed.add_field(name='❯ Issues', value=data.get(
                'open_issues_count'), inline=True)
            embed.add_field(name='❯ Language', value=data.get(
                'language'), inline=True)
            embed.add_field(name='❯ License', value=data.get(
                'license').get('spdx_id'), inline=True)
            embed.add_field(name='❯ Updated', value=data.get('updated_at').replace('T', ' ').replace('Z', ' '),
                            inline=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.channel.send(embed=embed)

    @commands.command(name='ping', aliases=['latency'], usage='ping', ignore_extra=False)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx: Context):
        """Checks the latency of the bot."""
        embed = nextcord.Embed(title='Pong!', description=f'Latency: `{str(round(self.bot.latency * 1000))}ms`',
                               color=DEFAULT_EMBED_COLOR)
        await ctx.channel.send(embed=embed)


def setup(bot: AniSearchBot):
    bot.add_cog(Help(bot))
    log.info('Help cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Help cog unloaded')
