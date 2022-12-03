import enum
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.utils.http import get, HttpException
from anisearch.utils.menus import BaseView

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


class ProfileView(BaseView):
    def __init__(self, interaction: discord.Interaction, overview: discord.Embed, favorites: discord.Embed) -> None:
        super().__init__(interaction, timeout=180)
        self.overview = overview
        self.favorites = favorites

        self.on_overview.disabled = True

    def disable_unavailable_buttons(self) -> None:
        self.on_overview.disabled = not self.on_overview.disabled
        self.on_favorites.disabled = not self.on_favorites.disabled

    @discord.ui.button(label='Overview', emoji='\N{BUST IN SILHOUETTE}', style=discord.ButtonStyle.gray)
    async def on_overview(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.disable_unavailable_buttons()
        await interaction.response.edit_message(embed=self.overview, view=self)

    @discord.ui.button(label='Favorites', emoji='\N{WHITE MEDIUM STAR}', style=discord.ButtonStyle.gray)
    async def on_favorites(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.disable_unavailable_buttons()
        await interaction.response.edit_message(embed=self.favorites, view=self)

    @discord.ui.button(emoji='\N{WASTEBASKET}', style=discord.ButtonStyle.red)
    async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.close()


class Profile(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @staticmethod
    def get_anilist_embeds(data: Dict[str, Any]) -> Tuple[discord.Embed, discord.Embed]:
        overview = discord.Embed(title=data.get('name'), url=data.get('siteUrl'), color=0x4169E1)
        overview.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)
        overview.set_footer(text='Provided by https://anilist.co/ • Overview')

        if data.get('avatar').get('large'):
            overview.set_thumbnail(url=data.get('avatar').get('large'))

        if data.get('bannerImage'):
            overview.set_image(url=data.get('bannerImage'))

        if data.get('about'):
            overview.add_field(
                name='About',
                value=data.get('about')[:500] + '...' if len(data.get('about')) > 500 else data.get('about'),
                inline=False,
            )

        anime_count = data.get('statistics').get('anime').get('count')
        anime_score = data.get('statistics').get('anime').get('meanScore')
        anime_days = round(data.get('statistics').get('anime').get('minutesWatched') / 60 / 24, 2)
        anime_episodes = data.get('statistics').get('anime').get('episodesWatched')

        overview.add_field(
            name='Anime Stats',
            value=f'Anime Count: {anime_count}\nMean Score: {anime_score}\nDays Watched: {anime_days}\nEpisodes: {anime_episodes}',
            inline=True,
        )

        manga_count = data.get('statistics').get('manga').get('count')
        manga_score = data.get('statistics').get('manga').get('meanScore')
        manga_chapters = data.get('statistics').get('manga').get('chaptersRead')
        manga_volumes = data.get('statistics').get('manga').get('volumesRead')

        overview.add_field(
            name='Manga Stats',
            value=f'Manga Count: {manga_count}\nMean Score: {manga_score}\nChapters Read: {manga_chapters}\nVolumes Read: {manga_volumes}',
            inline=True,
        )

        overview.add_field(
            name='Anime List', value=f'https://anilist.co/user/{data.get("name")}/animelist', inline=False
        )
        overview.add_field(
            name='Manga List', value=f'https://anilist.co/user/{data.get("name")}/mangalist', inline=False
        )

        favorites = discord.Embed(title=data.get('name'), url=data.get('siteUrl'), color=0x4169E1)
        favorites.set_author(name='AniList Profile', icon_url=ANILIST_LOGO)
        favorites.set_footer(text='Provided by https://anilist.co/ • Favorites')

        if data.get('avatar').get('large'):
            favorites.set_thumbnail(url=data.get('avatar').get('large'))

        for k, v in data.get('favourites').items():
            if nodes := v.get('nodes'):
                entries = []

                for i in nodes:
                    if k == 'anime' or k == 'manga':
                        name = i.get('title').get('romaji')
                    elif k == 'characters' or k == 'staff':
                        name = i.get('name').get('full')
                    else:
                        name = i.get('name')

                    entries.append(f'[{name}]({i.get("siteUrl")})')

                total = 0

                for i, j in enumerate(entries):
                    total += len(j) + 3

                    if total >= 1024:
                        entries = entries[:i]
                        entries[i - 1] = entries[i - 1] + '...'
                        break

                value = ' • '.join(entries)
            else:
                value = 'N/A'

            favorites.add_field(name=f'Favorite {k.capitalize()}', value=value, inline=False)

        return overview, favorites

    @staticmethod
    def get_myanimelist_embeds(data: Dict[str, Any]) -> Tuple[discord.Embed, discord.Embed]:
        description = []

        if data.get('last_online'):
            last_online = datetime.strptime(data.get('last_online').replace('+00:00', ''), "%Y-%m-%dT%H:%M:%S")
            description.append(f'**Last Online:** {discord.utils.format_dt(last_online, "R")}')

        if data.get('gender'):
            description.append(f'**Gender:** {data.get("gender")}')

        if data.get('birthday'):
            birthday = datetime.strptime(data.get('birthday').replace('+00:00', ''), "%Y-%m-%dT%H:%M:%S")
            description.append(f'**Birthday:** {discord.utils.format_dt(birthday, "R")}')

        if data.get('location'):
            description.append(f'**Location:** {data.get("location")}')

        if data.get('joined'):
            joined = datetime.strptime(data.get('joined').replace('+00:00', ''), "%Y-%m-%dT%H:%M:%S")
            description.append(f'**Joined:** {discord.utils.format_dt(joined, "R")}')

        overview = discord.Embed(
            title=data.get('username'), description='\n'.join(description), url=data.get('url'), color=0x4169E1
        )
        overview.set_author(name='MyAnimeList Profile', icon_url=MYANIMELIST_LOGO)
        overview.set_footer(text='Provided by https://myanimelist.net/ • Overview')

        if data.get('images').get('jpg').get('image_url') is not None:
            overview.set_thumbnail(url=data.get('images').get('jpg').get('image_url'))

        if data.get('about'):
            overview.add_field(
                name='About',
                value=data.get('about')[:500] + '...' if len(data.get('about')) > 500 else data.get('about'),
                inline=False,
            )

        anime_stats_data = data.get('statistics').get('anime')
        anime_stats = [
            f'Days Watched: {anime_stats_data.get("days_watched")}',
            f'Mean Score: {anime_stats_data.get("mean_score")}',
            f'Watching: {anime_stats_data.get("watching")}',
            f'Completed: {anime_stats_data.get("completed")}',
            f'On-Hold: {anime_stats_data.get("on_hold")}',
            f'Dropped: {anime_stats_data.get("dropped")}',
            f'Plan to Watch: {anime_stats_data.get("plan_to_watch")}',
            f'Total Entries: {anime_stats_data.get("total_entries")}',
            f'Rewatched: {anime_stats_data.get("rewatched")}',
            f'Episodes: {anime_stats_data.get("episodes_watched")}',
        ]
        overview.add_field(name='Anime Stats', value='\n'.join(anime_stats), inline=True)

        manga_stats_data = data.get('statistics').get('manga')
        manga_stats = [
            f'Days Read: {manga_stats_data.get("days_read")}',
            f'Mean Score: {manga_stats_data.get("mean_score")}',
            f'Reading: {manga_stats_data.get("reading")}',
            f'Completed: {manga_stats_data.get("completed")}',
            f'On-Hold: {manga_stats_data.get("on_hold")}',
            f'Dropped: {manga_stats_data.get("dropped")}',
            f'Plan to Read: {manga_stats_data.get("plan_to_read")}',
            f'Total Entries: {manga_stats_data.get("total_entries")}',
            f'Reread: {manga_stats_data.get("reread")}',
            f'Chapters Read: {manga_stats_data.get("chapters_read")}',
            f'Volumes Read: {manga_stats_data.get("volumes_read")}',
        ]
        overview.add_field(name='Manga Stats', value='\n'.join(manga_stats), inline=True)

        overview.add_field(
            name='Anime List', value=f'https://myanimelist.net/animelist/{data.get("username")}', inline=False
        )
        overview.add_field(
            name='Manga List', value=f'https://myanimelist.net/mangalist/{data.get("username")}', inline=False
        )

        favorites = discord.Embed(title=data.get('username'), url=data.get('url'), color=0x4169E1)
        favorites.set_author(name='MyAnimeList Profile', icon_url=MYANIMELIST_LOGO)
        favorites.set_footer(text='Provided by https://myanimelist.net/ • Favorites')

        if data.get('images').get('jpg').get('image_url') is not None:
            favorites.set_thumbnail(url=data.get('images').get('jpg').get('image_url'))

        for k, v in data.get('favorites').items():
            if v:
                entries = []

                for i in v:
                    if k == 'anime' or k == 'manga':
                        name = i.get('title')
                    else:
                        name = i.get('name')

                    entries.append(f'[{name}]({i.get("url")})')

                total = 0

                for i, j in enumerate(entries):
                    total += len(j) + 3

                    if total >= 1024:
                        entries = entries[:i]
                        entries[i - 1] = entries[i - 1] + '...'
                        break

                value = ' • '.join(entries)
            else:
                value = 'N/A'

            favorites.add_field(name=f'Favorite {k.capitalize()}', value=value, inline=False)

        return overview, favorites

    @app_commands.command(
        name='anilist', description='Displays information about the given AniList profile such as stats and favorites'
    )
    @app_commands.describe(username='Look up by username', member='Look up by server member')
    async def anilist_slash_command(
        self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None
    ):
        await interaction.response.defer()

        if username:
            data = await self.bot.anilist.user(page=1, perPage=1, name=username)

        else:
            user = member or interaction.user

            if profile := await self.bot.db.get_user_profile(user.id, str(AnimePlatform.AniList).lower()):
                data = await self.bot.anilist.user(page=1, perPage=1, id=profile.get('profile_id'))
            else:
                embed = discord.Embed(title=f':no_entry: No AniList profile added.', color=0x4169E1)
                return await interaction.followup.send(embed=embed)

        if data:
            overview, favorites = self.get_anilist_embeds(data[0])

            view = ProfileView(interaction=interaction, overview=overview, favorites=favorites)
            await interaction.followup.send(embed=overview, view=view)

        else:
            embed = discord.Embed(title=f':no_entry: The AniList profile could not be found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='myanimelist',
        description='Displays information about the given MyAnimeList profile such as stats and favorites',
    )
    @app_commands.describe(username='Look up by username', member='Look up by server member')
    async def myanimelist_slash_command(
        self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None
    ):
        await interaction.response.defer()

        if username:
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

        else:
            user = member or interaction.user

            if profile := await self.bot.db.get_user_profile(user.id, str(AnimePlatform.MyAnimeList).lower()):
                try:
                    user = (
                        (
                            await get(
                                url=f'https://api.jikan.moe/v4/users/userbyid/{profile.get("profile_id")}',
                                session=self.bot.session,
                                res_method='json',
                            )
                        )
                        .get('data')
                        .get('username')
                    )

                    data = (
                        await get(
                            url=f'https://api.jikan.moe/v4/users/{user}/full',
                            session=self.bot.session,
                            res_method='json',
                        )
                    ).get('data')
                except HttpException as e:
                    if not e.status == 404:
                        raise e
                    data = None
            else:
                embed = discord.Embed(title=f':no_entry: No MyAnimeList profile added.', color=0x4169E1)
                return await interaction.followup.send(embed=embed)

        if data:
            overview, favorites = self.get_myanimelist_embeds(data)

            view = ProfileView(interaction=interaction, overview=overview, favorites=favorites)
            await interaction.followup.send(embed=overview, view=view)

        else:
            embed = discord.Embed(title=f':no_entry: The MyAnimeList profile could not be found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)

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
        if await self.bot.db.get_user_profile(interaction.user.id, str(platform).lower()):
            await self.bot.db.remove_user_profile(interaction.user.id, str(platform).lower())

            embed = discord.Embed(
                title=f':white_check_mark: The added {str(platform)} profile has been removed.', color=0x4169E1
            )
        else:
            embed = discord.Embed(title=f':no_entry: You have not added a {str(platform)} profile.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)

    @profile_group.command(name='info', description='Displays the added profiles of you or a server member')
    async def profile_info_slash_command(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        user = member or interaction.user

        embed = discord.Embed(title=user.name, color=0x4169E1)
        embed.set_author(name='Profiles')
        embed.set_thumbnail(url=user.display_avatar)

        for i in AnimePlatform:
            if data := await self.bot.db.get_user_profile(user.id, str(i).lower()):
                embed.add_field(
                    name=str(i),
                    value=f'ID: {data.get("profile_id")}\nAdded: {discord.utils.format_dt(data.get("added_at"), "R")}',
                    inline=False,
                )
            else:
                embed.add_field(name=str(i), value='*Not added*', inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Profile(bot))
