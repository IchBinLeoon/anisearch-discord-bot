import logging
import time
from datetime import timedelta
from typing import Optional, Literal, List

import discord
from discord import app_commands
from discord.ext import commands

import anisearch
from anisearch.bot import AniSearchBot
from anisearch.utils.http import get
from anisearch.utils.menus import BaseView

log = logging.getLogger(__name__)

BOT_INVITE = 'https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=92224&scope=bot%20applications.commands'
SERVER_INVITE = 'https://discord.gg/Bv94yQYZM8'
WEBSITE = 'https://ichbinleoon.github.io/anisearch-discord-bot/'

CATEGORIES = Literal['Search', 'Image', 'Utility', 'Help']

COMMANDS = Literal[
    'anime',
    'manga',
    'character',
    'staff',
    'studio',
    'random',
    'waifu',
    'neko',
    'shinobu',
    'megumin',
    'avatar',
    'userinfo',
    'serverinfo',
    'help',
    'stats',
    'github',
    'ping',
    'invite',
    'support',
]


class Category:
    def __init__(self, label: str, emoji: str, embed: discord.Embed):
        self.label = label
        self.emoji = emoji
        self.embed = embed


class HelpView(BaseView):
    def __init__(self, interaction: discord.Interaction, home: discord.Embed, categories: List[Category]) -> None:
        super().__init__(interaction, timeout=180)
        self.add_item(CategorySelect(categories))
        self.home = home

    @discord.ui.button(label='Back', emoji='\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def on_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable_back_button(True)
        await interaction.response.edit_message(embed=self.home, view=self)

    async def disable_back_button(self, disabled: bool) -> None:
        self.on_back.disabled = disabled


class CategorySelect(discord.ui.Select):
    def __init__(self, categories: List[Category]) -> None:
        super().__init__(
            placeholder='Choose a category...',
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=i.label, emoji=i.emoji) for i in categories],
        )
        self.categories = categories

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.disable_back_button(False)
        embed = self.categories[[i.label for i in self.categories].index(self.values[0])].embed
        await interaction.response.edit_message(embed=embed, view=self.view)


def _label_to_emoji(label: str) -> str:
    emojis = {
        'Search': '\N{RIGHT-POINTING MAGNIFYING GLASS}',
        'Image': '\N{FRAME WITH PICTURE}',
        'Utility': '\N{HAMMER AND WRENCH}',
        'Help': '\N{BLACK QUESTION MARK ORNAMENT}',
    }
    return emojis[label]


class SocialsView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(label='Invite AniSearch', emoji='\N{LINK SYMBOL}', url=BOT_INVITE))
        self.add_item(discord.ui.Button(label='Support Server', emoji='\N{HANDSHAKE}', url=SERVER_INVITE))
        self.add_item(discord.ui.Button(label='Website', emoji='\N{GLOBE WITH MERIDIANS}', url=WEBSITE))


class LinkView(discord.ui.View):
    def __init__(self, label: str, emoji: str, url: str) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))


class Help(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @app_commands.command(name='help', description='Browse all commands of the bot')
    @app_commands.describe(category='Browse a specific command category', command='Look up a specific command')
    async def help_slash_command(
        self,
        interaction: discord.Interaction,
        category: Optional[CATEGORIES] = None,
        command: Optional[COMMANDS] = None,
    ):
        categories = []

        for i in self.bot.cogs:
            cog = self.bot.get_cog(i)

            if cmds := cog.get_app_commands():
                label = cog.qualified_name
                emoji = _label_to_emoji(label)

                embed = discord.Embed(title=f'{emoji} {label}', color=0x4169E1)
                embed.set_author(name='AniSearch Category', icon_url=self.bot.user.display_avatar)

                for j in cmds:
                    embed.add_field(name=f'/{j.qualified_name}', value=f'`{j.description}`', inline=False)

                categories.append(Category(label=label, emoji=emoji, embed=embed))

        home = discord.Embed(
            title=':books: Help',
            description=f'[Invite AniSearch]({BOT_INVITE}) | [Support Server]({SERVER_INVITE}) | [Website]({WEBSITE})',
            color=0x4169E1,
        )
        home.set_author(name='AniSearch Bot', icon_url=self.bot.user.display_avatar)
        home.set_thumbnail(url=self.bot.user.display_avatar)

        for i in categories:
            cmds = self.bot.get_cog(i.label).get_app_commands()
            home.add_field(name=f'{i.emoji} {i.label}', value=', '.join([f'`{i.name}`' for i in cmds]), inline=False)

        if command:
            cmds = []
            for i in self.bot.cogs:
                for j in self.bot.get_cog(i).walk_app_commands():
                    cmds.append(j)

            cmd = discord.utils.get(cmds, name=command)

            embed = discord.Embed(title=f'» {cmd.qualified_name} «', colour=0x4169E1)
            embed.set_author(name='AniSearch Command', icon_url=self.bot.user.display_avatar)
            embed.add_field(name=f'/{cmd.qualified_name}', value=f'`{cmd.description}`', inline=False)

        elif category:
            embed = categories[[i.label for i in categories].index(category)].embed
        else:
            embed = home

        view = HelpView(interaction=interaction, home=home, categories=categories)

        if not command and not category:
            await view.disable_back_button(True)

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='stats', description='Displays information and statistics about the bot')
    async def stats_slash_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=':bar_chart: Information & Statistics',
            description=f'This instance of the bot is owned by {(await self.bot.application_info()).owner.mention}',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name='AniSearch Stats', icon_url=self.bot.user.display_avatar)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Servers', value=len(self.bot.guilds), inline=True)
        embed.add_field(name='❯ Users', value=sum([i.member_count for i in self.bot.guilds]), inline=True)
        embed.add_field(name='❯ Channels', value=sum([len(i.channels) for i in self.bot.guilds]), inline=True)
        embed.add_field(name='❯ Uptime', value=timedelta(seconds=round(time.time() - self.bot.start_time)), inline=True)
        embed.add_field(name='❯ Shards', value=self.bot.shard_count, inline=True)
        embed.add_field(name='❯ Latency', value=round(self.bot.latency, 5), inline=True)
        embed.add_field(name='❯ Commands', value='/help', inline=True)
        embed.add_field(name='❯ Version', value=f'v{anisearch.__version__}', inline=True)
        embed.add_field(name='❯ Creator', value='<@!223871059068321793>', inline=True)

        await interaction.response.send_message(embed=embed, view=SocialsView())

    @app_commands.command(name='github', description='Displays information about the GitHub repository')
    async def github_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = await get(
            url='https://api.github.com/repos/IchBinLeoon/anisearch-discord-bot',
            session=self.bot.session,
            res_method='json',
        )

        embed = discord.Embed(
            title=data.get('full_name'),
            url=data.get('html_url'),
            description=data.get('description'),
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name='AniSearch GitHub', icon_url=self.bot.user.display_avatar)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Stargazers', value=data.get('stargazers_count'), inline=True)
        embed.add_field(name='❯ Forks', value=data.get('forks_count'), inline=True)
        embed.add_field(name='❯ Issues', value=data.get('open_issues_count'), inline=True)
        embed.add_field(name='❯ Language', value=data.get('language'), inline=True)
        embed.add_field(name='❯ License', value=data.get('license').get('spdx_id'), inline=True)
        embed.add_field(name='❯ Size', value=f'{round(data.get("size") / 1024, 2)} MB', inline=True)

        view = LinkView(label='Visit the Repository', emoji='\N{GLOBE WITH MERIDIANS}', url=data.get('html_url'))
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='ping', description='Checks the latency of the bot')
    async def ping_slash_command(self, interaction: discord.Interaction):
        shards = '\n'.join([f'[SHARD #{i[0]}] {round(i[1] * 1000)}ms' for i in self.bot.latencies])

        embed = discord.Embed(
            title=':ping_pong: Pong!',
            description=f'Latency: `{round(self.bot.latency * 1000)}ms`\n```ini\n{shards}\n```',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='invite', description='Invite the bot to your server')
    async def invite_slash_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=':link: Invite AniSearch',
            description='Thanks for your interest! :heart:',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Invite AniSearch to Your Server', emoji='\N{LINK SYMBOL}', url=BOT_INVITE)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='support', description='Join the bot support server')
    async def support_slash_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=':handshake: Support Server',
            description='Head to the support server! :shield:',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Join the Support Server', emoji='\N{HANDSHAKE}', url=SERVER_INVITE)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Help(bot))
