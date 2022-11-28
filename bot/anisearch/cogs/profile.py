import enum
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)

ANILIST_LOGO = 'https://cdn.discordapp.com/attachments/978016869342658630/978033399107289189/anilist.png'
MYANIMELIST_LOGO = 'https://cdn.discordapp.com/attachments/978016869342658630/978033442816143390/myanimelist.png'
KITSU_LOGO = 'https://cdn.discordapp.com/attachments/978016869342658630/978033462776840232/kitsu.png'


class AnimePlatform(enum.Enum):
    AniList = 0
    MyAnimeList = 1
    Kitsu = 2

    def __str__(self) -> str:
        return self.name


class Profile(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @app_commands.command(
        name='anilist', description='Displays information about the given AniList profile such as stats and favorites'
    )
    @app_commands.describe(username='Look up by username', member='Look up by server member')
    async def anilist_slash_command(
        self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None
    ):
        await interaction.response.defer()

        await interaction.followup.send('anilist')

    @app_commands.command(
        name='myanimelist',
        description='Displays information about the given MyAnimeList profile such as stats and favorites',
    )
    @app_commands.describe(username='Look up by username', member='Look up by server member')
    async def myanimelist_slash_command(
        self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None
    ):
        await interaction.response.defer()

        await interaction.followup.send('myanimelist')

    @app_commands.command(
        name='kitsu', description='Displays information about the given Kitsu profile such as stats and favorites'
    )
    @app_commands.describe(username='Look up by username', member='Look up by server member')
    async def kitsu_slash_command(
        self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None
    ):
        await interaction.response.defer()

        await interaction.followup.send('kitsu')

    profile_group = app_commands.Group(
        name='profile', description='AniList, MyAnimeList and Kitsu profile management commands'
    )

    @profile_group.command(name='add', description='Adds an AniList, MyAnimeList or Kitsu profile to your account')
    @app_commands.describe(platform='The anime tracking site', username='Your site username')
    async def profile_add_slash_command(self, interaction: discord.Interaction, platform: AnimePlatform, username: str):
        await interaction.response.defer()

        await interaction.followup.send('profile add')

    @profile_group.command(
        name='remove', description='Removes an added AniList, MyAnimeList or Kitsu profile from your account'
    )
    @app_commands.describe(platform='The anime tracking site')
    async def profile_remove_slash_command(self, interaction: discord.Interaction, platform: AnimePlatform):
        await interaction.response.send_message('profile remove')

    @profile_group.command(name='info', description='Displays the added profiles of you or a server member')
    async def profile_info_slash_command(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        await interaction.response.send_message('profile info')


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Profile(bot))
