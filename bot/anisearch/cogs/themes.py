import logging
from typing import Optional, List

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
            'include[anime]': 'images,animethemes.animethemeentries.videos,animethemes.song',
        }

        if (
            data := (
                await get(
                    url='https://api.animethemes.moe/search/',
                    session=self.bot.session,
                    res_method='json',
                    params=params,
                )
            )
            .get('search')
            .get('anime')
        ):
            embeds = []

            for page, anime in enumerate(data, start=1):
                embed = discord.Embed(
                    title=anime.get('name'), color=0x4169E1, url=f'https://animethemes.moe/anime/{anime.get("slug")}'
                )
                embed.set_author(name='Anime Themes')
                embed.set_thumbnail(url=anime.get('images')[0].get('link'))
                embed.set_footer(text=f'Provided by https://animethemes.moe/ • Page {page}/{len(data)}')

                for i in anime.get('animethemes'):
                    if not i.get('nsfw') and i.get('animethemeentries'):
                        link = f'https://v.animethemes.moe/{i.get("animethemeentries")[0].get("videos")[0].get("basename")}'

                        embed.add_field(
                            name=f'{i.get("slug")} • {i.get("id")}',
                            value=f'[{i.get("song").get("title")}]({link})' if i.get('song') else link,
                            inline=False,
                        )

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
                raise e
            data = None

        if data and not data.get('animethemeentries')[0].get('nsfw'):
            description = f'**Title:** {data.get("song").get("title")}'

            if data.get('song').get('artists'):
                description += f'\n**Artists:** {", ".join([i.get("name") for i in data.get("song").get("artists")])}'

            embed = discord.Embed(title=data.get('anime').get('name'), description=description, color=0x4169E1)
            embed.set_author(name=data.get('slug').replace('OP', 'Opening ').replace('ED', 'Ending '))
            embed.set_thumbnail(url=data.get('anime').get('images')[0].get('link'))
            embed.set_footer(text='Provided by https://animethemes.moe/')

            await interaction.followup.send(embed=embed)

            await interaction.followup.send(
                f'https://v.animethemes.moe/{data.get("animethemeentries")[0].get("videos")[0].get("basename")}'
            )
        else:
            embed = discord.Embed(title=f':no_entry: No theme with the ID `{animethemes_id}` found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Themes(bot))
