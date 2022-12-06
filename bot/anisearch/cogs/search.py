import asyncio
import datetime
import logging
import random
from typing import List, Dict, Any, Optional, Literal

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.cogs.profile import ANILIST_LOGO
from anisearch.utils.anilist import GENRES, TAGS
from anisearch.utils.formatters import (
    format_media_format,
    format_anime_status,
    format_manga_status,
    format_media_source,
    format_media_title,
    sanitize_description,
    format_date,
    format_name,
    month_to_season,
)
from anisearch.utils.menus import PaginationView, SimplePaginationView

log = logging.getLogger(__name__)


async def comma_separated_choices(arr: List[str], current: str) -> List[app_commands.Choice[str]]:
    incomplete, choices = current.split(',')[-1].strip(), []

    for i in arr:
        if incomplete.lower() in i.lower():
            choice = ', '.join([i.strip().capitalize() for i in current.split(',')[:-1]] + [i])

            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices[:25]


async def genres_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return await comma_separated_choices(arr=GENRES, current=current)


async def tags_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return await comma_separated_choices(arr=TAGS, current=current)


class SearchView(PaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class SimpleSearchView(SimplePaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[List[discord.Embed]]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class Search(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @staticmethod
    def get_media_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=format_media_title(data.get('title').get('romaji'), data.get('title').get('english')),
            description=sanitize_description(data.get('description'), 400),
            color=discord.Color.from_str(data.get('coverImage').get('color') or '0x4169E1'),
            url=data.get('siteUrl'),
        )
        embed.set_author(name=format_media_format(data.get('format')), icon_url=ANILIST_LOGO)
        embed.set_footer(text=f'Provided by https://anilist.co/')

        if data.get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('coverImage').get('large'))

        if data.get('bannerImage'):
            embed.set_image(url=data.get('bannerImage'))

        if data.get('type') == 'ANIME':
            if data.get('status') == 'RELEASING':

                if data.get('episodes'):
                    aired_episodes = f'{data.get("nextAiringEpisode").get("episode") - 1}/{data.get("episodes")}'
                else:
                    aired_episodes = data.get('nextAiringEpisode').get('episode') - 1

                if data.get('nextAiringEpisode').get('airingAt'):
                    airing_at = discord.utils.format_dt(
                        datetime.datetime.fromtimestamp(data.get('nextAiringEpisode').get('airingAt')), 'R'
                    )
                else:
                    airing_at = 'N/A'

                embed.add_field(name='Aired Episodes', value=f'{aired_episodes} (Next {airing_at})', inline=False)
            else:
                embed.add_field(name='Episodes', value=data.get('episodes') or 'N/A', inline=False)
        else:
            embed.add_field(name='Chapters', value=data.get('chapters') or 'N/A', inline=True)
            embed.add_field(name='Volumes', value=data.get('volumes') or 'N/A', inline=True)
            embed.add_field(name='Source', value=format_media_source(data.get('source')), inline=True)

        if data.get('type') == 'ANIME':
            status = format_anime_status(data.get('status'))
        else:
            status = format_manga_status(data.get('status'))

        embed.add_field(name='Status', value=status, inline=True)

        start_date = format_date(
            data.get('startDate').get('day'),
            data.get('startDate').get('month'),
            data.get('startDate').get('year'),
        )
        end_date = format_date(
            data.get('endDate').get('day'),
            data.get('endDate').get('month'),
            data.get('endDate').get('year'),
        )
        embed.add_field(name='Start Date', value=start_date, inline=True)
        embed.add_field(name='End Date', value=end_date, inline=True)

        if data.get('type') == 'ANIME':
            if data.get('duration'):
                duration = f'{data.get("duration")} {"min" if data.get("episodes") == 1 else "min each"}'
            else:
                duration = 'N/A'

            studio = data.get('studios').get('nodes')[0].get('name') if data.get('studios').get('nodes') else 'N/A'

            embed.add_field(name='Duration', value=duration, inline=True)
            embed.add_field(name='Studio', value=studio, inline=True)
            embed.add_field(name='Source', value=format_media_source(data.get('source')), inline=True)

        embed.add_field(name='Score', value=data.get("meanScore") or 'N/A', inline=True)
        embed.add_field(name='Popularity', value=data.get("popularity") or 'N/A', inline=True)
        embed.add_field(name='Favourites', value=data.get("favourites") or 'N/A', inline=True)

        if data.get('genres'):
            embed.add_field(name='Genres', value=', '.join([f'`{i}`' for i in data.get('genres')]), inline=False)

        sites = [f'[AniList]({data.get("siteUrl")})']

        if data.get('idMal'):
            sites.append(f'[MyAnimeList](https://myanimelist.net/anime/{data.get("idMal")})')

        embed.add_field(name='Find Out More', value=' • '.join(sites), inline=False)

        return embed

    @staticmethod
    def get_character_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=format_name(data.get('name').get('full'), data.get('name').get('native')),
            description=sanitize_description(data.get('description'), 1000),
            color=0x4169E1,
            url=data.get('siteUrl'),
        )
        embed.set_author(name='Character', icon_url=ANILIST_LOGO)
        embed.set_footer(text=f'Provided by https://anilist.co/')

        if data.get('image').get('large'):
            embed.set_thumbnail(url=data.get('image').get('large'))

        birthday = format_date(
            data.get('dateOfBirth').get('day'),
            data.get('dateOfBirth').get('month'),
            data.get('dateOfBirth').get('year'),
        )

        embed.add_field(name='Birthday', value=birthday, inline=True)
        embed.add_field(name='Age', value=data.get('age') or 'N/A', inline=True)
        embed.add_field(name='Gender', value=data.get('gender') or 'N/A', inline=True)

        if synonyms := [f'`{i}`' for i in data.get('name').get('alternative')] + [
            f'||`{i}`||' for i in data.get('name').get('alternativeSpoiler')
        ]:
            embed.add_field(name='Synonyms', value=', '.join(synonyms), inline=False)

        if media := [
            f'[{i.get("title").get("romaji")}]({i.get("siteUrl")})'
            for i in data.get('media').get('nodes')
            if not i.get('isAdult')
        ]:
            embed.add_field(name='Popular Appearances', value=' • '.join(media), inline=False)

        return embed

    @staticmethod
    def get_staff_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=format_name(data.get('name').get('full'), data.get('name').get('native')),
            description=sanitize_description(data.get('description'), 1000),
            color=0x4169E1,
            url=data.get('siteUrl'),
        )
        embed.set_author(name='Staff', icon_url=ANILIST_LOGO)
        embed.set_footer(text=f'Provided by https://anilist.co/')

        if data.get('image').get('large'):
            embed.set_thumbnail(url=data.get('image').get('large'))

        birthday = format_date(
            data.get('dateOfBirth').get('day'),
            data.get('dateOfBirth').get('month'),
            data.get('dateOfBirth').get('year'),
        )

        embed.add_field(name='Birthday', value=birthday, inline=True)
        embed.add_field(name='Age', value=data.get('age') or 'N/A', inline=True)
        embed.add_field(name='Gender', value=data.get('gender') or 'N/A', inline=True)
        embed.add_field(name='Hometown', value=data.get('homeTown') or 'N/A', inline=True)
        embed.add_field(name='Language', value=data.get('languageV2') or 'N/A', inline=True)

        if occupations := data.get('primaryOccupations'):
            embed.add_field(name='Primary Occupations', value=', '.join(occupations), inline=True)

        if synonyms := [f'`{i}`' for i in data.get('name').get('alternative')]:
            embed.add_field(name='Synonyms', value=', '.join(synonyms), inline=False)

        if staff_roles := [
            f'[{i.get("title").get("romaji")}]({i.get("siteUrl")})'
            for i in data.get('staffMedia').get('nodes')
            if not i.get('isAdult')
        ]:
            embed.add_field(name='Popular Staff Roles', value=' • '.join(staff_roles), inline=False)

        if character_roles := [
            f'[{i.get("name").get("full")}]({i.get("siteUrl")})' for i in data.get('characters').get('nodes')
        ]:
            embed.add_field(name='Popular Character Roles', value=' • '.join(character_roles), inline=False)

        return embed

    @staticmethod
    def get_studio_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(title=data.get('name'), color=0x4169E1, url=data.get('siteUrl'))
        embed.set_author(name='Studio', icon_url=ANILIST_LOGO)
        embed.set_footer(text=f'Provided by https://anilist.co/')

        if data.get('isAnimationStudio'):
            embed.description = '**Animation Studio**'

        if nodes := data.get('media').get('nodes'):
            if not nodes[0].get('isAdult'):
                embed.set_thumbnail(url=nodes[0].get('coverImage').get('large'))

            media = []
            for i in nodes:
                if not i.get('isAdult'):
                    anime = (
                        f'[{i.get("title").get("romaji")}]({i.get("siteUrl")}) » '
                        f'**{format_media_format(i.get("format"))}** • Episodes: **{i.get("episodes") or "N/A"}** '
                    )
                    media.append(anime)

            if media:
                embed.add_field(name='Most Popular Productions', value='\n'.join(media), inline=False)

        return embed

    @staticmethod
    def get_simple_media_embed(data: Dict[str, Any]) -> discord.Embed:
        description = []

        if data.get('type') == 'ANIME':
            description.append(f'**Status:** {format_anime_status(data.get("status"))}')
            description.append(f'**Episodes:** {data.get("episodes") or "N/A"}')
            studio = data.get('studios').get('nodes')[0].get('name') if data.get('studios').get('nodes') else 'N/A'
            description.append(f'**Studio:** {studio}')
            description.append(f'**Score:** {data.get("meanScore") or "N/A"}')
        else:
            description.append(f'**Status:** {format_manga_status(data.get("status"))}')
            description.append(f'**Chapters:** {data.get("chapters") or "N/A"}')
            description.append(f'**Volumes:** {data.get("volumes") or "N/A"}')
            description.append(f'**Score:** {data.get("meanScore") or "N/A"}')

        sites = [f'[AniList]({data.get("siteUrl")})']

        if data.get('idMal'):
            sites.append(f'[MyAnimeList](https://myanimelist.net/anime/{data.get("idMal")})')

        description.append(f'\n{" • ".join(sites)}')

        embed = discord.Embed(
            title=data.get('title').get('romaji'),
            description='\n'.join(description),
            color=discord.Color.from_str(data.get('coverImage').get('color') or '0x4169E1'),
            url=data.get('siteUrl'),
        )
        embed.set_author(name=format_media_format(data.get('format')), icon_url=ANILIST_LOGO)
        embed.set_footer(text=f'Provided by https://anilist.co/')

        if data.get('coverImage').get('large'):
            embed.set_thumbnail(url=data.get('coverImage').get('large'))

        return embed

    @app_commands.command(
        name='anime',
        description='Searches for an anime with the given title and displays information about the search results',
    )
    @app_commands.describe(title='The title of the anime to search for', limit='The number of results to return')
    async def anime_slash_command(
        self, interaction: discord.Interaction, title: str, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        if data := await self.bot.anilist.media(page=1, perPage=limit, type='ANIME', isAdult=False, search=title):
            embeds = []

            for page, anime in enumerate(data, start=1):
                embed = self.get_media_embed(anime)
                embed.set_footer(text=f'{embed.footer.text} • Page {page}/{len(data)}')

                embeds.append(embed)

            view = SearchView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(
                title=f':no_entry: An anime with the title `{title}` could not be found.', color=0x4169E1
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='manga',
        description='Searches for a manga with the given title and displays information about the search results',
    )
    @app_commands.describe(title='The title of the manga to search for', limit='The number of results to return')
    async def manga_slash_command(
        self, interaction: discord.Interaction, title: str, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        if data := await self.bot.anilist.media(page=1, perPage=limit, type='MANGA', isAdult=False, search=title):
            embeds = []

            for page, manga in enumerate(data, start=1):
                embed = self.get_media_embed(manga)
                embed.set_footer(text=f'{embed.footer.text} • Page {page}/{len(data)}')

                embeds.append(embed)

            view = SearchView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(
                title=f':no_entry: A manga with the title `{title}` could not be found.', color=0x4169E1
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='character',
        description='Searches for a character with the given name and displays information about the search results',
    )
    @app_commands.describe(name='The name of the character to search for', limit='The number of results to return')
    async def character_slash_command(
        self, interaction: discord.Interaction, name: str, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        if data := await self.bot.anilist.character(page=1, perPage=limit, search=name):
            embeds = []

            for page, character in enumerate(data, start=1):
                embed = self.get_character_embed(character)
                embed.set_footer(text=f'{embed.footer.text} • Page {page}/{len(data)}')

                embeds.append(embed)

            view = SearchView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(
                title=f':no_entry: A character with the name `{name}` could not be found.', color=0x4169E1
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='staff',
        description='Searches for a staff with the given name and displays information about the search results',
    )
    @app_commands.describe(name='The name of the staff to search for', limit='The number of results to return')
    async def staff_slash_command(
        self, interaction: discord.Interaction, name: str, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        if data := await self.bot.anilist.staff(page=1, perPage=limit, search=name):
            embeds = []

            for page, staff in enumerate(data, start=1):
                embed = self.get_staff_embed(staff)
                embed.set_footer(text=f'{embed.footer.text} • Page {page}/{len(data)}')

                embeds.append(embed)

            view = SearchView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(
                title=f':no_entry: A staff with the name `{name}` could not be found.', color=0x4169E1
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='studio',
        description='Searches for a studio with the given name and displays information about the search results',
    )
    @app_commands.describe(name='The name of the studio to search for', limit='The number of results to return')
    async def studio_slash_command(
        self, interaction: discord.Interaction, name: str, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        if data := await self.bot.anilist.studio(page=1, perPage=limit, search=name):
            embeds = []

            for page, studio in enumerate(data, start=1):
                embed = self.get_studio_embed(studio)
                embed.set_footer(text=f'{embed.footer.text} • Page {page}/{len(data)}')

                embeds.append(embed)

            view = SearchView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(
                title=f':no_entry: A studio with the name `{name}` could not be found.', color=0x4169E1
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name='random', description='Displays a random anime or manga')
    @app_commands.describe(
        media='The type of the media', genres='A comma separated list of genres', tags='A comma separated list of tags'
    )
    @app_commands.autocomplete(genres=genres_autocomplete, tags=tags_autocomplete)
    async def random_slash_command(
        self,
        interaction: discord.Interaction,
        media: Optional[Literal['Anime', 'Manga']] = None,
        genres: Optional[str] = None,
        tags: Optional[str] = None,
    ):
        await interaction.response.defer()

        media = media or random.choice(['Anime', 'Manga'])

        if genres:
            genres = [i.strip() for i in genres.split(',')]

        if tags:
            tags = [i.strip() for i in tags.split(',')]

        page, limit, result = random.randrange(1, 1000), 1, None

        for i in range(0, 3):
            if data := await self.bot.anilist.media(
                page=page,
                perPage=limit,
                type=media.upper(),
                isAdult=False,
                genres=genres,
                tags=tags,
                sort='POPULARITY_DESC',
            ):
                if i < 2:
                    result = data[0]
                else:
                    result = data[random.randrange(0, len(data))]
                break
            else:
                if i < 1:
                    page = round(page / 3)
                else:
                    page, limit = 1, 50

                await asyncio.sleep(1)

        if result:
            embed = self.get_media_embed(result)
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(title=f':no_entry: A random media could not be found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name='trending', description='Displays the current trending anime or manga')
    @app_commands.describe(media='The type of the media')
    async def trending_slash_command(self, interaction: discord.Interaction, media: Literal['Anime', 'Manga']):
        await interaction.response.defer()

        data, embeds = (
            await self.bot.anilist.media(page=1, perPage=15, type=media.upper(), isAdult=False, sort='TRENDING_DESC'),
            [],
        )

        for rank, anime in enumerate(data, start=1):
            embed = self.get_simple_media_embed(anime)
            embed.set_author(name=f'{embed.author.name} • #{rank} Trending {media}', icon_url=ANILIST_LOGO)

            embeds.append(embed)

        view = SimpleSearchView(interaction=interaction, embeds=[embeds[i : i + 3] for i in range(0, len(embeds), 3)])
        await interaction.followup.send(embeds=embeds[0:3], view=view)

    @app_commands.command(name='seasonal', description='Displays the currently airing anime')
    async def seasonal_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        date = datetime.datetime.now()

        season = month_to_season(date.month)
        year = date.year

        data, embeds = (
            await self.bot.anilist.media(
                season=season, seasonYear=year, page=1, type='ANIME', isAdult=False, sort='POPULARITY_DESC'
            ),
            [],
        )

        for anime in data:
            embed = self.get_simple_media_embed(anime)
            embed.set_author(name=f'{embed.author.name} • {season} {year}', icon_url=ANILIST_LOGO)

            embeds.append(embed)

        view = SimpleSearchView(interaction=interaction, embeds=[embeds[i : i + 3] for i in range(0, len(embeds), 3)])
        await interaction.followup.send(embeds=embeds[0:3], view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Search(bot))
