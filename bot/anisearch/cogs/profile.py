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

                embed = discord.Embed(title=f'Added AniList Profile `{data[0].get("name")}`', color=0x4169E1)
                embed.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)
                embed.set_footer(text='Provided by https://anilist.co/')

                if data[0].get('avatar').get('large'):
                    embed.set_thumbnail(url=data[0].get('avatar').get('large'))

                anime_count = data[0].get('statistics').get('anime').get('count')
                anime_score = data[0].get('statistics').get('anime').get('meanScore')
                anime_days = round(data[0].get('statistics').get('anime').get('minutesWatched') / 60 / 24, 2)

                embed.add_field(
                    name='Anime Stats',
                    value=f'Anime Count: {anime_count}\nMean Score: {anime_score}\nDays Watched: {anime_days}',
                    inline=True,
                )

                manga_count = data[0].get('statistics').get('manga').get('count')
                manga_score = data[0].get('statistics').get('manga').get('meanScore')
                manga_chapters = data[0].get('statistics').get('manga').get('chaptersRead')

                embed.add_field(
                    name='Manga Stats',
                    value=f'Manga Count: {manga_count}\nMean Score: {manga_score}\nChapters Read: {manga_chapters}',
                    inline=True,
                )

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

                embed = discord.Embed(title=f'Added MyAnimeList Profile `{data.get("username")}`', color=0x4169E1)
                embed.set_author(name='MyAnimeList Profile', icon_url=MYANIMELIST_LOGO)
                embed.set_footer(text='Provided by https://myanimelist.net/')

                if data.get('images').get('jpg').get('image_url') is not None:
                    embed.set_thumbnail(url=data.get('images').get('jpg').get('image_url'))

                anime_days = data.get('statistics').get('anime').get('days_watched')
                anime_score = data.get('statistics').get('anime').get('mean_score')
                anime_entries = data.get('statistics').get('anime').get('total_entries')

                embed.add_field(
                    name='Anime Stats',
                    value=f'Days Watched: {anime_days}\nMean Score: {anime_score}\nTotal Entries: {anime_entries}',
                    inline=True,
                )

                manga_days = data.get('statistics').get('manga').get('days_read')
                manga_score = data.get('statistics').get('manga').get('mean_score')
                manga_entries = data.get('statistics').get('manga').get('total_entries')

                embed.add_field(
                    name='Manga Stats',
                    value=f'Days Read: {manga_days}\nMean Score: {manga_score}\nTotal Entries: {manga_entries}',
                    inline=True,
                )

                return await interaction.followup.send(embed=embed)

        if platform == AnimePlatform.Kitsu:
            if data := (
                await get(
                    url='https://kitsu.io/api/edge/users',
                    session=self.bot.session,
                    res_method='json',
                    params={'filter[name]': username, 'include': 'stats'},
                )
            ):
                await self.bot.db.add_user_profile(
                    interaction.user.id, str(platform).lower(), int(data.get('data')[0].get('id'))
                )

                embed = discord.Embed(
                    title=f'Added Kitsu Profile `{data.get("data")[0].get("attributes").get("name")}`', color=0x4169E1
                )
                embed.set_author(name='Kitsu Profile', icon_url=KITSU_LOGO)
                embed.set_footer(text='Provided by https://kitsu.io/')

                if data.get('data')[0].get('attributes').get('avatar').get('original'):
                    embed.set_thumbnail(url=data.get('data')[0].get('attributes').get('avatar').get('original'))

                for i in data.get('included'):
                    if i.get('attributes').get('kind') == 'anime-amount-consumed':
                        episodes = i.get('attributes').get('statsData').get('units')
                        completed = i.get('attributes').get('statsData').get('completed')
                        entries = i.get('attributes').get('statsData').get('media')

                        embed.add_field(
                            name='Anime Stats',
                            value=f'Episodes: {episodes}\nCompleted: {completed}\nTotal Entries: {entries}',
                            inline=True,
                        )

                    if i.get('attributes').get('kind') == 'manga-amount-consumed':
                        chapters = i.get('attributes').get('statsData').get('units')
                        completed = i.get('attributes').get('statsData').get('completed')
                        entries = i.get('attributes').get('statsData').get('media')

                        embed.add_field(
                            name='Manga Stats',
                            value=f'Chapters: {chapters}\nCompleted: {completed}\nTotal Entries: {entries}',
                            inline=True,
                        )

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
