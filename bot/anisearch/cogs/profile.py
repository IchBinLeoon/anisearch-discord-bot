import enum
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.utils.http import get, HttpException

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

        if platform == AnimePlatform.AniList:
            if data := await self.bot.anilist.user(page=1, perPage=1, name=username):
                await self.bot.db.add_user_profile(interaction.user.id, str(platform).lower(), data[0].get('id'))

                embed = discord.Embed(title=data[0].get('name'))

                return await interaction.followup.send(embed=embed)

        if platform == AnimePlatform.MyAnimeList:
            try:
                data = (
                    await get(
                        url=f'https://api.jikan.moe/v4/users/{username}/full',
                        session=self.bot.session,
                        res_method='json',
                    )
                ).get('data')
            except HttpException as e:
                if not e.status == 404:
                    raise e
                data = None

            if data:
                await self.bot.db.add_user_profile(interaction.user.id, str(platform).lower(), data.get('mal_id'))

                embed = discord.Embed(title=data.get('username'))

                return await interaction.followup.send(embed=embed)

        if platform == AnimePlatform.Kitsu:
            if data := (
                await get(
                    url='https://kitsu.io/api/edge/users',
                    session=self.bot.session,
                    res_method='json',
                    params={'filter[name]': username},
                )
            ).get('data'):
                await self.bot.db.add_user_profile(interaction.user.id, str(platform).lower(), int(data[0].get('id')))

                embed = discord.Embed(title=data[0].get('attributes').get('name'))

                return await interaction.followup.send(embed=embed)

        embed = discord.Embed(
            title=f':no_entry: The {str(platform)} profile `{username}` could not be found.', color=0x4169E1
        )
        await interaction.followup.send(embed=embed)

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
