import logging
from typing import Optional, List, Dict, Any

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.utils.http import get
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

            embed.add_field(name=i.get('slug'), value='\n'.join(info), inline=False)

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


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Themes(bot))
