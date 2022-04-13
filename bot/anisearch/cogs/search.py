import logging
import random
from typing import Union, List, Dict, Any, Optional

import nextcord
from nextcord import Embed, Interaction, SlashOption
from nextcord.ext import commands
from nextcord.ext.commands import Context

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import is_adult
from anisearch.utils.constants import ERROR_EMBED_COLOR, DEFAULT_EMBED_COLOR, ANILIST_LOGO
from anisearch.utils.types import AniListSearchType, AniListMediaType
from anisearch.utils.formatters import format_description, format_date, format_media_type, format_anime_status, \
    format_manga_status
from anisearch.utils.menus import EmbedListButtonMenu, SearchButtonMenuPages

log = logging.getLogger(__name__)


class Search(commands.Cog, name='Search'):

    def __init__(self, bot: AniSearchBot):
        self.bot = bot

    async def anilist_search(self, ctx: Union[Context, Interaction], search: str, type_: str) -> Union[List[Embed], None]:
        embeds = []
        data = None

        try:
            if type_ == AniListSearchType.Anime:
                data = await self.bot.anilist.media(search=search, page=1, perPage=15, type=type_.upper())
            elif type_ == AniListSearchType.Manga:
                data = await self.bot.anilist.media(search=search, page=1, perPage=15, type=type_.upper())
            elif type_ == AniListSearchType.Character:
                data = await self.bot.anilist.character(search=search, page=1, perPage=15)
            elif type_ == AniListSearchType.Staff:
                data = await self.bot.anilist.staff(search=search, page=1, perPage=15)
            elif type_ == AniListSearchType.Studio:
                data = await self.bot.anilist.studio(search=search, page=1, perPage=15)

        except Exception as e:
            log.exception(e)

            embed = nextcord.Embed(
                title=f'An error occurred while searching for the {type_.lower()} `{search}`. Try again.',
                color=ERROR_EMBED_COLOR)
            embeds.append(embed)

            return embeds

        if data is not None:
            for page, entry in enumerate(data):

                embed = None

                try:
                    if type_ == AniListSearchType.Anime:
                        embed = await self.get_media_embed(entry, page + 1, len(data))
                    elif type_ == AniListSearchType.Manga:
                        embed = await self.get_media_embed(entry, page + 1, len(data))
                    elif type_ == AniListSearchType.Character:
                        embed = await self.get_character_embed(entry, page + 1, len(data))
                    elif type_ == AniListSearchType.Staff:
                        embed = await self.get_staff_embed(entry, page + 1, len(data))
                    elif type_ == AniListSearchType.Studio:
                        embed = await self.get_studio_embed(entry, page + 1, len(data))

                    if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                        if is_adult(entry) and not ctx.channel.is_nsfw():
                            embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                                   description=f'Adult content. No NSFW channel.')
                            embed.set_footer(
                                text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                except Exception as e:
                    log.exception(e)

                    embed = nextcord.Embed(
                        title='Error', color=ERROR_EMBED_COLOR,
                        description=f'An error occurred while loading the embed for the {type_.lower()}.')
                    embed.set_footer(
                        text=f'Provided by https://anilist.co/ • Page {page + 1}/{len(data)}')

                embeds.append(embed)

            return embeds
        return None

    async def anilist_random(self, ctx: Union[Context, Interaction], search: str, type_: str, format_in: List[str]) -> Union[Embed, None]:
        try:

            data = await self.bot.anilist.genre(genre=search, page=1, perPage=1, type=type_,
                                                format_in=format_in)

            if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:
                page = random.randrange(1, data.get(
                    'data')['Page']['pageInfo']['lastPage'])
                data = await self.bot.anilist.genre(genre=search, page=page, perPage=1, type=type_,
                                                    format_in=format_in)

            else:

                data = await self.bot.anilist.tag(tag=search, page=1, perPage=1, type=type_,
                                                  format_in=format_in)

                if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:
                    page = random.randrange(1, data.get(
                        'data')['Page']['pageInfo']['lastPage'])
                    data = await self.bot.anilist.tag(tag=search, page=page, perPage=1, type=type_,
                                                      format_in=format_in)
                else:
                    return None

        except Exception as e:
            log.exception(e)

            embed = nextcord.Embed(
                title=f'An error occurred while searching for a {type_.lower()} with the genre `{search}`.',
                color=ERROR_EMBED_COLOR)

            return embed

        if data.get('data')['Page']['media'] is not None and len(data.get('data')['Page']['media']) > 0:

            try:
                embed = await self.get_media_embed(data.get('data')['Page']['media'][0])

                if not isinstance(ctx.channel, nextcord.channel.DMChannel):
                    if is_adult(data.get('data')['Page']['media'][0]) and not ctx.channel.is_nsfw():
                        embed = nextcord.Embed(title='Error', color=ERROR_EMBED_COLOR,
                                               description=f'Adult content. No NSFW channel.')

            except Exception as e:
                log.exception(e)

                embed = nextcord.Embed(
                    title=f'An error occurred while searching for a {type_.lower()} with the genre `{search}`.',
                    color=ERROR_EMBED_COLOR)

            return embed

        return None

    @staticmethod
    async def get_media_embed(data: Dict[str, Any], page: Optional[int] = None, pages: Optional[int] = None) -> Embed:
        embed = nextcord.Embed(description=format_description(data.get('description'), 400)
                               if data.get('description') else 'N/A',
                               colour=int('0x' + data.get('coverImage')
                               ['color'].replace('#', ''), 0)
                               if data.get('coverImage')['color'] else DEFAULT_EMBED_COLOR)

        if data.get('title')['english'] is None or data.get('title')['english'] == data.get('title')['romaji']:
            embed.title = data.get('title')['romaji']
        else:
            embed.title = f'{data.get("title")["romaji"]} ({data.get("title")["english"]})'

        if data.get('coverImage')['large']:
            embed.set_thumbnail(url=data.get('coverImage')['large'])

        if data.get('bannerImage'):
            embed.set_image(url=data.get('bannerImage'))

        stats = []
        try:
            type_ = f'Type: {format_media_type(data.get("format")) if data.get("format") else "N/A"}'
        except KeyError:
            type_ = f'Type: N/A'
        stats.append(type_)

        status = 'Status: N/A'
        try:
            if data.get('type') == 'ANIME':
                status = f'Status: {format_anime_status(data.get("status"))}'
            elif data.get('type') == 'MANGA':
                status = f'Status: {format_manga_status(data.get("status"))}'
        except KeyError:
            pass
        stats.append(status)

        score = f'Score: {str(data.get("meanScore")) if data.get("meanScore") else "N/A"}'
        stats.append(score)

        embed.set_author(name=' | '.join(stats), icon_url=ANILIST_LOGO)

        if data.get('type') == 'ANIME':
            if data.get('status') == 'RELEASING':
                try:
                    if data.get('nextAiringEpisode')['episode']:
                        aired_episodes = str(
                            data.get('nextAiringEpisode')['episode'] - 1)
                        next_episode_time = 'N/A'
                        if data.get('nextAiringEpisode')['airingAt']:
                            next_episode_time = f'<t:{data.get("nextAiringEpisode")["airingAt"]}:R>'
                        embed.add_field(name='Aired Episodes', value=f'{aired_episodes} (Next {next_episode_time})',
                                        inline=True)
                except TypeError:
                    embed.add_field(name='Episodes', value=data.get('episodes') if data.get('episodes') else 'N/A',
                                    inline=True)
            else:
                embed.add_field(name='Episodes', value=data.get('episodes') if data.get('episodes') else 'N/A',
                                inline=True)

        elif data.get('type') == 'MANGA':
            embed.add_field(name='Chapters', value=data.get(
                'chapters') if data.get('chapters') else 'N/A', inline=True)
            embed.add_field(name='Volumes', value=data.get(
                'volumes') if data.get('volumes') else 'N/A', inline=True)
            embed.add_field(name='Source', inline=True,
                            value=data.get('source').replace('_', ' ').title() if data.get('source') else 'N/A')

        if data.get('startDate')['day']:
            try:
                start_date = format_date(data.get('startDate')['day'], data.get('startDate')['month'],
                                         data.get('startDate')['year'])
                end_date = '?'
                if data.get('endDate')['day']:
                    end_date = format_date(data.get('endDate')['day'], data.get('endDate')['month'],
                                           data.get('endDate')['year'])
                embed.add_field(name='Aired' if data.get('type') == 'ANIME' else 'Published',
                                value=f'{start_date} to {end_date}', inline=False)
            except TypeError:
                embed.add_field(name='Aired' if data.get(
                    'type') == 'ANIME' else 'Published', value='N/A', inline=False)
        else:
            embed.add_field(name='Aired' if data.get('type') ==
                            'ANIME' else 'Published', value='N/A', inline=False)

        if data.get('type') == 'ANIME':
            duration = 'N/A'
            if data.get('duration'):
                duration = str(data.get(
                    'duration')) + ' {}'.format('min' if data.get('episodes') == 1 else 'min each')
            embed.add_field(name='Duration', value=duration, inline=True)
            embed.add_field(name='Source', value=data.get('source').replace('_', ' ').title() if data.get('source') else
                            'N/A', inline=True)
            embed.add_field(name='Studio', value=data.get('studios')['nodes'][0]['name'] if data.get('studios')['nodes']
                            else 'N/A', inline=True)

        if data.get('synonyms'):
            embed.add_field(name='Synonyms', value=', '.join(
                [f'`{s}`' for s in data.get('synonyms')]), inline=False)

        embed.add_field(name='Genres', inline=False,
                        value=', '.join([f'`{g}`' for g in data.get('genres')] if data.get('genres') else 'N/A'))

        sites = []
        if data.get('trailer'):
            if data.get('trailer')['site'] == 'youtube':
                sites.append(
                    f'[Trailer](https://www.youtube.com/watch?v={data.get("trailer")["id"]})')
        if data.get('externalLinks'):
            for i in data.get('externalLinks'):
                sites.append(f'[{i["site"]}]({i["url"]})')
        embed.add_field(name='Streaming and external sites' if data.get('type') == 'ANIME' else 'External sites',
                        value=' | '.join(sites) if len(sites) > 0 else 'N/A', inline=False)

        sites = []
        if data.get('siteUrl'):
            sites.append(f'[Anilist]({data.get("siteUrl")})')
            embed.url = data.get('siteUrl')
        if data.get('idMal'):
            sites.append(
                f'[MyAnimeList](https://myanimelist.net/anime/{str(data.get("idMal"))})')
        embed.add_field(name='Find out more', value=' | '.join(
            sites) if len(sites) > 0 else 'N/A', inline=False)

        if page is not None and pages is not None:
            embed.set_footer(
                text=f'Provided by https://anilist.co/ • Page {page}/{pages}')
        else:
            embed.set_footer(text=f'Provided by https://anilist.co/')

        return embed

    @staticmethod
    async def get_character_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = nextcord.Embed(
            color=DEFAULT_EMBED_COLOR,
            description=format_description(data.get('description'), 1000) if data.get('description') else 'N/A')

        if data.get('name')['full'] is None or data.get('name')['full'] == data.get('name')['native']:
            embed.title = data.get('name')['native']
        elif data.get('name')['native'] is None:
            embed.title = data.get('name')['full']
        else:
            embed.title = f'{data.get("name")["full"]} ({data.get("name")["native"]})'

        embed.set_author(name='Character', icon_url=ANILIST_LOGO)

        if data.get('image')['large']:
            embed.set_thumbnail(url=data.get('image')['large'])

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if len(data.get('name')['alternative']) > 0:
            embed.add_field(name='Synonyms', inline=False,
                            value=', '.join([f'`{a}`' for a in data.get('name')['alternative']]))

        if data.get('media')['nodes']:
            media = []
            for x in data.get('media')['nodes']:
                media.append(
                    f'[{[x][0]["title"]["romaji"]}]({[x][0]["siteUrl"]})')

            if len(media) > 5:
                media = media[0:5]
                media[4] = media[4] + '...'

            embed.add_field(name='Appearances',
                            value=' | '.join(media), inline=False)

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_staff_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = nextcord.Embed(
            color=DEFAULT_EMBED_COLOR,
            description=format_description(data.get('description'), 1000) if data.get('description') else 'N/A')

        if data.get('name')['full'] is None or data.get('name')['full'] == data.get('name')['native']:
            embed.title = data.get('name')['native']
        elif data.get('name')['native'] is None:
            embed.title = data.get('name')['full']
        else:
            embed.title = f'{data.get("name")["full"]} ({data.get("name")["native"]})'

        embed.set_author(name='Staff', icon_url=ANILIST_LOGO)

        if data.get('image')['large']:
            embed.set_thumbnail(url=data.get('image')['large'])

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if data.get('staffMedia')['nodes']:
            staff_roles = []
            for x in data.get('staffMedia')['nodes']:
                staff_roles.append(
                    f'[{[x][0]["title"]["romaji"]}]({[x][0]["siteUrl"]})')

            if len(staff_roles) > 5:
                staff_roles = staff_roles[0:5]
                staff_roles[4] += '...'

            embed.add_field(name='Staff Roles', value=' | '.join(
                staff_roles), inline=False)

        if data.get('characters')['nodes']:
            character_roles = []
            for x in data.get('characters')['nodes']:
                character_roles.append(
                    f'[{[x][0]["name"]["full"]}]({[x][0]["siteUrl"]})')

            if len(character_roles) > 5:
                character_roles = character_roles[0:5]
                character_roles[4] += '...'

            embed.add_field(name='Character Roles', value=' | '.join(
                character_roles), inline=False)

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @staticmethod
    async def get_studio_embed(data: Dict[str, Any], page: int, pages: int) -> Embed:
        embed = nextcord.Embed(color=DEFAULT_EMBED_COLOR,
                               title=data.get('name'))

        embed.set_author(name='Studio', icon_url=ANILIST_LOGO)

        if data.get('siteUrl'):
            embed.url = data.get('siteUrl')

        if data.get('media')['nodes']:
            if data.get('media')['nodes'][0]['coverImage']['large']:
                embed.set_thumbnail(url=data.get('media')[
                    'nodes'][0]['coverImage']['large'])

        if data.get('isAnimationStudio') is True:
            embed.description = '**Animation Studio**'

        if data.get('media')['nodes']:
            media, length = [], 0
            for x in data.get('media')['nodes']:
                studio = f'[{[x][0]["title"]["romaji"]}]({[x][0]["siteUrl"]}) » Type: ' \
                         f'**{format_media_type([x][0]["format"]) if [x][0]["format"] else "N/A"}** | Episodes: ' \
                         f'**{[x][0]["episodes"] if [x][0]["episodes"] else "N/A"}**'
                length += len(studio)
                if length >= 1024:
                    break
                media.append(studio)

            embed.add_field(name='Most Popular Productions',
                            value='\n'.join(media), inline=False)

        embed.set_footer(
            text=f'Provided by https://anilist.co/ • Page {page}/{pages}')

        return embed

    @commands.command(name='anime', aliases=['a', 'ani'], usage='anime <title>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def anime(self, ctx: Context, *, title: str):
        """Searches for an anime with the given title and displays information about the search results such as type,
        status, episodes, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(ctx, title, AniListSearchType.Anime)
            if embeds:
                menu = SearchButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'The anime `{title}` could not be found.', color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='manga', aliases=['m'], usage='manga <title>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def manga(self, ctx: Context, *, title: str):
        """Searches for a manga with the given title and displays information about the search results such as type,
        status, chapters, description, and more!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(ctx, title, AniListSearchType.Manga)
            if embeds:
                menu = SearchButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'The manga `{title}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='character', aliases=['char'], usage='character <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def character(self, ctx: Context, *, name: str):
        """Searches for a character with the given name and displays information about the search results such as
        description, synonyms, and appearances!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(ctx, name, AniListSearchType.Character)
            if embeds:
                menu = SearchButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'The character `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='staff', usage='staff <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def staff(self, ctx: Context, *, name: str):
        """Searches for a staff with the given name and displays information about the search results such as
        description, staff roles, and character roles!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(ctx, name, AniListSearchType.Staff)
            if embeds:
                menu = SearchButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'The staff `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='studio', usage='studio <name>', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def studio(self, ctx: Context, *, name: str):
        """Searches for a studio with the given name and displays information about the search results such as the
        studio productions!"""
        async with ctx.channel.typing():
            embeds = await self.anilist_search(ctx, name, AniListSearchType.Studio)
            if embeds:
                menu = SearchButtonMenuPages(
                    source=EmbedListButtonMenu(embeds),
                    clear_buttons_after=True,
                    timeout=60,
                    style=nextcord.ButtonStyle.primary
                )
                await menu.start(ctx)
            else:
                embed = nextcord.Embed(
                    title=f'The studio `{name}` could not be found.',
                    color=ERROR_EMBED_COLOR)
                await ctx.channel.send(embed=embed)

    @commands.command(name='random', usage='random <anime|manga> <genre>', ignore_extra=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def random(self, ctx: Context, media: str, *, genre: str):
        """Displays a random anime or manga of the specified genre."""
        async with ctx.channel.typing():
            if media.lower() == AniListMediaType.Anime.lower():
                embed = await self.anilist_random(ctx, genre, AniListMediaType.Anime.upper(),
                                                  ['TV', 'MOVIE', 'OVA', 'ONA', 'TV_SHORT', 'MUSIC', 'SPECIAL'])
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = nextcord.Embed(title=f'An anime with the genre `{genre}` could not be found.',
                                           color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            elif media.lower() == AniListMediaType.Manga.lower():
                embed = await self.anilist_random(ctx, genre, AniListMediaType.Manga.upper(),
                                                  ['MANGA', 'ONE_SHOT', 'NOVEL'])
                if embed:
                    await ctx.channel.send(embed=embed)
                else:
                    embed = nextcord.Embed(title=f'A manga with the genre `{genre}` could not be found.',
                                           color=ERROR_EMBED_COLOR)
                    await ctx.channel.send(embed=embed)
            else:
                ctx.command.reset_cooldown(ctx)
                raise nextcord.ext.commands.BadArgument

    @nextcord.slash_command(
        name='anime',
        description='Searches for an anime with the given title and displays information about the search results'
    )
    async def anime_slash_command(
            self,
            interaction: nextcord.Interaction,
            title: str = SlashOption(
                description='The title of the anime',
                required=True
            )
    ):
        embeds = await self.anilist_search(interaction, title, AniListSearchType.Anime)
        if embeds:
            pages = SearchButtonMenuPages(
                source=EmbedListButtonMenu(embeds),
                clear_buttons_after=True,
                timeout=60,
                style=nextcord.ButtonStyle.primary
            )
            await pages.start(interaction=interaction)
        else:
            embed = nextcord.Embed(
                title=f'An anime with the title `{title}` could not be found.',
                color=ERROR_EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='manga',
        description='Searches for a manga with the given title and displays information about the search results'
    )
    async def manga_slash_command(
            self,
            interaction: nextcord.Interaction,
            title: str = SlashOption(
                description='The title of the manga',
                required=True
            )
    ):
        embeds = await self.anilist_search(interaction, title, AniListSearchType.Manga)
        if embeds:
            pages = SearchButtonMenuPages(
                source=EmbedListButtonMenu(embeds),
                clear_buttons_after=True,
                timeout=60,
                style=nextcord.ButtonStyle.primary
            )
            await pages.start(interaction=interaction)
        else:
            embed = nextcord.Embed(
                title=f'A manga with the title `{title}` could not be found.',
                color=ERROR_EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='character',
        description='Searches for a character with the given name and displays information about the search results'
    )
    async def character_slash_command(
            self,
            interaction: nextcord.Interaction,
            name: str = SlashOption(
                description='The name of the character',
                required=True
            )
    ):
        embeds = await self.anilist_search(interaction, name, AniListSearchType.Character)
        if embeds:
            pages = SearchButtonMenuPages(
                source=EmbedListButtonMenu(embeds),
                clear_buttons_after=True,
                timeout=60,
                style=nextcord.ButtonStyle.primary
            )
            await pages.start(interaction=interaction)
        else:
            embed = nextcord.Embed(
                title=f'A character with the name `{name}` could not be found.',
                color=ERROR_EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='staff',
        description='Searches for a staff with the given name and displays information about the search results'
    )
    async def staff_slash_command(
            self,
            interaction: nextcord.Interaction,
            name: str = SlashOption(
                description='The name of the staff',
                required=True
            )
    ):
        embeds = await self.anilist_search(interaction, name, AniListSearchType.Staff)
        if embeds:
            pages = SearchButtonMenuPages(
                source=EmbedListButtonMenu(embeds),
                clear_buttons_after=True,
                timeout=60,
                style=nextcord.ButtonStyle.primary
            )
            await pages.start(interaction=interaction)
        else:
            embed = nextcord.Embed(
                title=f'A staff with the name `{name}` could not be found.',
                color=ERROR_EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='studio',
        description='Searches for a studio with the given name and displays information about the search results'
    )
    async def studio_slash_command(
            self,
            interaction: nextcord.Interaction,
            name: str = SlashOption(
                description='The name of the studio',
                required=True
            )
    ):
        embeds = await self.anilist_search(interaction, name, AniListSearchType.Studio)
        if embeds:
            pages = SearchButtonMenuPages(
                source=EmbedListButtonMenu(embeds),
                clear_buttons_after=True,
                timeout=60,
                style=nextcord.ButtonStyle.primary
            )
            await pages.start(interaction=interaction)
        else:
            embed = nextcord.Embed(
                title=f'A studio with the name `{name}` could not be found.',
                color=ERROR_EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='random',
        description='Displays a random anime or manga of the specified genre'
    )
    async def random_slash_command(
            self,
            interaction: nextcord.Interaction,
            media: str = SlashOption(
                description='The type of the media',
                required=True,
                choices=['Anime', 'Manga']
            ),
            genre: str = SlashOption(
                description='The name of the genre',
                required=True,
                choices=[
                    'Action',
                    'Adventure',
                    'Comedy',
                    'Drama',
                    'Ecchi',
                    'Fantasy',
                    'Horror',
                    'Mahou Shoujo',
                    'Mecha',
                    'Music',
                    'Mystery',
                    'Psychological',
                    'Romance',
                    'Sci-Fi',
                    'Slice of Life',
                    'Sports',
                    'Supernatural',
                    'Thriller'
                ]
            )
    ):
        embed = await self.anilist_random(interaction, genre, media.upper(), ['TV', 'MOVIE', 'OVA', 'ONA', 'TV_SHORT',
                                                                              'MUSIC', 'SPECIAL', 'MANGA', 'ONE_SHOT',
                                                                              'NOVEL'])
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            embed = nextcord.Embed(
                title=f'{"An" if media == "Anime" else "A"} {media.lower()} with the genre `{genre}` '
                      f'could not be found.',
                color=ERROR_EMBED_COLOR)
            await interaction.response.send_message(embed=embed)


def setup(bot: AniSearchBot):
    bot.add_cog(Search(bot))
    log.info('Search cog loaded')


def teardown(bot: AniSearchBot):
    log.info('Search cog unloaded')
