import logging
from typing import Optional, List, Dict, Any

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.utils.http import get, HttpException
from anisearch.utils.menus import PaginationView

log = logging.getLogger(__name__)


class ThemesView(PaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class Themes(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @staticmethod
    def get_themes_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=data.get('name'), color=0x4169E1, url=f'https://animethemes.moe/anime/{data.get("slug")}'
        )
        embed.set_author(name='Anime Themes')
        embed.set_thumbnail(url=data.get('images')[0].get('link'))
        embed.set_footer(text='Provided by https://animethemes.moe/')

        for i in data.get('animethemes'):
            info = ['**Title:** ' + i.get('song').get('title')]

            if i.get('song').get('artists'):
                info.append('**Artist:** ' + i.get('song').get('artists')[0].get('name'))

            try:
                info.append(
                    f'[Link](https://v.animethemes.moe/{i.get("animethemeentries")[0].get("videos")[0].get("basename")})'
                )
            except IndexError:
                pass

            embed.add_field(name=f'{i.get("slug")} • {i.get("id")}', value='\n'.join(info), inline=False)

        return embed

    @staticmethod
    def get_theme_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(title=data.get('anime').get('name'), color=0x4169E1)
        embed.set_author(name=data.get('slug').replace('OP', 'Opening ').replace('ED', 'Ending '))
        embed.set_thumbnail(url=data.get('anime').get('images')[0].get('link'))
        embed.set_footer(text='Provided by https://animethemes.moe/')

        info = ['**Title:** ' + data.get('song').get('title')]

        if data.get('song').get('artists'):
            info.append('**Artist:** ' + ', '.join([i.get('name') for i in data.get('song').get('artists')]))

        embed.description = '\n'.join(info)

        return embed

    @app_commands.command(
        name='themes',
        description='Searches for the opening and ending themes of an anime',
    )
    @app_commands.describe(title='The title of the anime', limit='The number of results to return')
    async def themes_slash_command(
        self, interaction: discord.Interaction, title: str, limit: Optional[app_commands.Range[int, 1, 15]] = 10
    ):
        await interaction.response.defer()

        params = {
            'q': title,
            'page[limit]': limit,
            'fields[search]': 'anime',
            'include[anime]': 'images,animethemes.animethemeentries.videos,animethemes.song.artists',
        }

        data, entries = (
            (
                await get(
                    url='https://api.animethemes.moe/search/',
                    session=self.bot.session,
                    res_method='json',
                    params=params,
                )
            )
            .get('search')
            .get('anime')
        ), []

        for i in data:
            for j in i.get('animethemes'):
                for k in j.get('animethemeentries'):
                    if not k.get('nsfw'):
                        if i not in entries:
                            entries.append(i)

        if entries:
            embeds = []

            for k, v in enumerate(entries, start=1):
                embed = self.get_themes_embed(v)
                embed.set_footer(text=f'{embed.footer.text} • Page {k}/{len(entries)}')
                embeds.append(embed)

            view = ThemesView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(title=f':no_entry: No themes for the anime `{title}` found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name='theme', description='Displays a specific anime opening or ending theme')
    @app_commands.describe(animethemes_id='The AnimeThemes ID of the theme')
    @app_commands.rename(animethemes_id='id')
    async def theme_slash_command(self, interaction: discord.Interaction, animethemes_id: int):
        await interaction.response.defer()

        try:
            data = (
                await get(
                    url=f'https://api.animethemes.moe/animetheme/{animethemes_id}',
                    session=self.bot.session,
                    res_method='json',
                    params={'include': 'anime.images,animethemeentries.videos,song.artists'},
                )
            ).get('animetheme')
        except HttpException as e:
            if not e.status == 404:
                log.error(e)
            data = None

        if data and not data.get('animethemeentries')[0].get('nsfw'):
            embed = self.get_theme_embed(data)

            await interaction.followup.send(embed=embed)
            await interaction.followup.send(
                f'https://v.animethemes.moe/{data.get("animethemeentries")[0].get("videos")[0].get("basename")}'
            )
        else:
            embed = discord.Embed(title=f':no_entry: No theme with the ID `{animethemes_id}` found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Themes(bot))
