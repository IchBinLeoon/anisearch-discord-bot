import logging
import time
from datetime import timedelta, datetime
from typing import Optional, List

import nextcord
from nextcord import SlashOption
from nextcord.channel import DMChannel
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.utils import find

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.config import BOT_OWNER_ID
from anisearch.utils.constants import DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, DEFAULT_PREFIX, CREATOR_ID, BOT_ID, \
    DISCORD_INVITE, WEBSITE, GITHUB_REPO_API_ENDPOINT, SUPPORT_SERVER_INVITE
from anisearch.utils.http import get
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
            if command := nextcord.utils.get(self.bot.commands, name=cmd.lower()) or \
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
            data = await get(url=GITHUB_REPO_API_ENDPOINT, session=self.bot.session, res_method='json')
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

    @nextcord.slash_command(name='help', description='Shows help or displays information about a command')
    async def help_slash_command(
            self,
            interaction: nextcord.Interaction,
            command: str = SlashOption(
                description='Look up a specific command',
                required=False
            )
    ):
        if command is not None:
            if cmd := nextcord.utils.get([i for i in self.bot.get_all_application_commands()], name=command.lower()):
                cmds = []

                if len(cmd.children) > 0:
                    for _, v in cmd.children.items():
                        cmds.append(v)
                else:
                    cmds.append(cmd)

                embed = nextcord.Embed(title=f'» `{cmd.qualified_name}`', colour=0x4169E1, timestamp=datetime.now())

                embed.set_author(name='AniSearch Command', icon_url=self.bot.user.display_avatar.url)
                embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

                for i in cmds:
                    name = f'/{i.qualified_name}'

                    if len(i.checks) >= 1:
                        name += ' :shield:'
                        embed.description = ':shield: = This command can be used only in a server'

                    if len(i.checks) >= 2:
                        name += ' :lock:'
                        embed.description = ':shield: = This command can be used only in a server\n' \
                                            ':lock: = This command can be used only by a server administrator'

                    embed.add_field(name=name, value=i.description, inline=False)

                return await interaction.response.send_message(embed=embed)

        embed = nextcord.Embed(
            title='AniSearch',
            description=f'**Command help:**\n`/help`\n\n'
                        f'**Command list:**\n`/commands`\n\n**Links:**\n'
                        f'[Invite AniSearch]({BOT_INVITE}) | '
                        f'[Support Server]({SERVER_INVITE}) | '
                        f'[Website](https://ichbinleoon.github.io/anisearch-discord-bot/)',
            color=0x4169E1
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name='commands', description='Browse all commands of the bot', guild_ids=[701168020160118896])
    async def commands_slash_command(
            self,
            interaction: nextcord.Interaction,
            category: str = SlashOption(
                description='Browse a specific command category',
                required=False,
                choices=['Search', 'Profile', 'Notification', 'Image', 'Themes', 'News', 'Help']
            )
    ):
        categories = []

        for i in self.bot.cogs:
            cog = self.bot.get_cog(i)

            if len(cog.to_register) > 0:
                label = cog.qualified_name
                emoji = _label_to_emoji(label)
                cmds = []

                embed = nextcord.Embed(title=f'{emoji} {label}', color=0x4169E1, timestamp=datetime.now())

                embed.set_author(name='AniSearch Category', icon_url=self.bot.user.display_avatar.url)
                embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

                for j in cog.to_register:
                    if len(j.children) > 0:
                        for _, v in j.children.items():
                            cmds.append(v)
                    else:
                        cmds.append(j)

                for j in cmds:
                    name = f'/{j.qualified_name}'

                    if len(j.checks) >= 1:
                        name += ' :shield:'
                        embed.description = ':shield: = This command can be used only in a server'

                    if len(j.checks) >= 2:
                        name += ' :lock:'
                        embed.description = ':shield: = This command can be used only in a server\n' \
                                            ':lock: = This command can be used only by a server administrator'

                    embed.add_field(name=name, value=f'`{j.description}`', inline=False)

                categories.append(CommandsCategory(label=label, emoji=emoji, embed=embed))

        if category:
            embed = categories[[i.label for i in categories].index(category)].embed
        else:
            embed = categories[0].embed

        view = CommandsView(user=interaction.user, categories=categories)
        await interaction.response.send_message(embed=embed, view=view)

    @nextcord.slash_command(name='stats', description='Displays information and statistics about the bot')
    async def stats_slash_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title=':bar_chart: Information & Statistics',
            description=f'This instance of the bot is owned by {(await self.bot.application_info()).owner.mention}',
            color=0x4169E1,
            timestamp=datetime.now()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name='AniSearch Bot', icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Guilds', value=len(self.bot.guilds), inline=True)
        embed.add_field(name='❯ Users', value=sum([i.member_count for i in self.bot.guilds]), inline=True)
        embed.add_field(name='❯ Channels', value=sum([len(i.channels) for i in self.bot.guilds]), inline=True)

        embed.add_field(
            name='❯ Uptime',
            value=timedelta(seconds=round(time.time() - self.bot.start_time)),
            inline=True
        )

        embed.add_field(name='❯ Shards', value=self.bot.shard_count, inline=True)
        embed.add_field(name='❯ Version', value=f'v{anisearch.__version__}', inline=True)
        embed.add_field(name='❯ Creator', value=f'<@!223871059068321793>', inline=False)

        view = LinkView(label='Invite AniSearch to Your Server', url=BOT_INVITE)
        await interaction.response.send_message(embed=embed, view=view)

    @nextcord.slash_command(name='github', description='Displays information about the GitHub repository')
    async def github_slash_command(self, interaction: nextcord.Interaction):
        data = await get(
            url='https://api.github.com/repos/IchBinLeoon/anisearch-discord-bot',
            session=self.bot.session,
            res_method='json'
        )

        embed = nextcord.Embed(
            title=data.get('full_name'),
            url=data.get('html_url'),
            description=data.get('description'),
            color=0x4169E1,
            timestamp=datetime.now()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name='GitHub Repository')
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Stargazers', value=data.get('stargazers_count'), inline=True)
        embed.add_field(name='❯ Forks', value=data.get('forks_count'), inline=True)
        embed.add_field(name='❯ Issues', value=data.get('open_issues_count'), inline=True)
        embed.add_field(name='❯ Language', value=data.get('language'), inline=True)
        embed.add_field(name='❯ License', value=data.get('license').get('spdx_id'), inline=True)

        embed.add_field(
            name='❯ Updated',
            value=f'<t:{int(datetime.strptime(data.get("pushed_at"), "%Y-%m-%dT%H:%M:%SZ").timestamp())}>',
            inline=True
        )

        view = LinkView(label='Visit the Repository', url=data.get('html_url'))
        await interaction.response.send_message(embed=embed, view=view)

    @nextcord.slash_command(name='ping', description='Checks the latency of the bot')
    async def ping_slash_command(self, interaction: nextcord.Interaction):
        shards = '\n'.join([f'[SHARD #{i[0]}] {round(i[1] * 1000)}ms' for i in self.bot.latencies])

        embed = nextcord.Embed(
            title=':ping_pong: Pong!',
            description=f'Latency: `{round(self.bot.latency * 1000)}ms`\n```ini\n{shards}\n```',
            color=0x4169E1,
            timestamp=datetime.now()
        )

        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name='invite', description='Invite the bot to your server')
    async def invite_slash_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title=':link: Invite AniSearch',
            description='Thanks for your interest! :heart:',
            color=0x4169E1,
            timestamp=datetime.now()
        )

        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Invite AniSearch to Your Server', url=BOT_INVITE)
        await interaction.response.send_message(embed=embed, view=view)

    @nextcord.slash_command(name='support', description='Join the bot support server')
    async def support_slash_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title=':handshake: Support Server',
            description='Head to the support server! :shield:',
            color=0x4169E1,
            timestamp=datetime.now()
        )

        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Join the Support Server', url=SERVER_INVITE)
        await interaction.response.send_message(embed=embed, view=view)


def _label_to_emoji(label: str) -> str:
    emojis = {
        'Search': '\N{RIGHT-POINTING MAGNIFYING GLASS}',
        'Profile': '\N{BUST IN SILHOUETTE}',
        'Notification': '\N{BELL}',
        'Image': '\N{FRAME WITH PICTURE}',
        'Themes': '\N{CLAPPER BOARD}',
        'News': '\N{NEWSPAPER}',
        'Help': '\N{BLACK QUESTION MARK ORNAMENT}',
    }
    return emojis[label]


class CommandsCategory:
    def __init__(self, label: str, emoji: str, embed: nextcord.Embed):
        self.label = label
        self.emoji = emoji
        self.embed = embed


class CommandsView(nextcord.ui.View):
    def __init__(self, user: nextcord.User, categories: List[CommandsCategory]):
        super().__init__(timeout=180)
        self.add_item(CommandsDropdown(categories))
        self._user = user

    async def interaction_check(self, interaction: nextcord.Interaction):
        return self._user == interaction.user


class CommandsDropdown(nextcord.ui.Select):
    def __init__(self, categories: List[CommandsCategory]):
        super().__init__(
            placeholder='Choose a category...',
            min_values=1,
            max_values=1,
            options=[nextcord.SelectOption(label=i.label, emoji=i.emoji) for i in categories]
        )
        self.categories = categories

    async def callback(self, interaction: nextcord.Interaction):
        embed = self.categories[[i.label for i in self.categories].index(self.values[0])].embed
        await interaction.message.edit(embed=embed)


class LinkView(nextcord.ui.View):
    def __init__(self, label: str, url: str):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=label, url=url))


BOT_INVITE = 'https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=92224&scope=bot%20applications.commands'
SERVER_INVITE = 'https://discord.gg/Bv94yQYZM8'


def setup(bot: AniSearchBot):
    bot.add_cog(Help(bot))
    log.info('Help cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Help cog unloaded')
