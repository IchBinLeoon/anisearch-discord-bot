import html
import logging
from typing import List, Dict, Any, Optional

import discord
from bs4 import BeautifulSoup
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from anisearch.bot import AniSearchBot
from anisearch.utils.formatters import clean_html
from anisearch.utils.http import get
from anisearch.utils.menus import SimplePaginationView

log = logging.getLogger(__name__)

ANIMENEWSNETWORK_LOGO = (
    'https://cdn.discordapp.com/attachments/978016869342658630/978033496410947625/animenewsnetwork.png'
)
CRUNCHYROLL_LOGO = 'https://cdn.discordapp.com/attachments/978016869342658630/978033539830403142/crunchyroll.png'


class NewsView(SimplePaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class News(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    async def parse_news_feed(self, url: str, limit: int) -> List[Dict[str, Any]]:
        text, data = await get(url=url, session=self.bot.session, res_method='text'), []

        for i in BeautifulSoup(text, 'xml').find_all('item'):
            if len(data) >= limit:
                break

            entry = {
                'title': i.find('title').text,
                'description': i.find('description').text,
                'link': i.find('guid').text,
                'category': getattr(i.find('category'), 'text', None),
                'date': i.find('pubDate').text,
            }
            data.append(entry)

        return data

    @staticmethod
    def get_aninews_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=data.get('title'),
            description=f'```{html.unescape(clean_html(data.get("description")))}```',
            color=0x4169E1,
            url=data.get('link'),
        )
        embed.set_footer(text='Provided by https://www.animenewsnetwork.com/')

        info = ['Anime News Network', data.get('date').replace('-0500', 'EST')]

        if data.get('category'):
            info.append(data.get('category'))

        embed.set_author(name=' • '.join(info), icon_url=ANIMENEWSNETWORK_LOGO)

        return embed

    @staticmethod
    def get_crunchynews_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=data.get('title'),
            description=f'```{html.unescape(clean_html(data.get("description")))}```',
            color=0x4169E1,
            url=data.get('link'),
        )
        embed.set_footer(text='Provided by https://www.crunchyroll.com/')
        embed.set_author(name=f'Crunchyroll • {data.get("date")}', icon_url=CRUNCHYROLL_LOGO)

        return embed

    @app_commands.command(name='aninews', description='Displays the latest anime news from Anime News Network')
    @app_commands.describe(limit='The number of results to return')
    async def aninews_slash_command(
        self, interaction: discord.Interaction, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        data, embeds = await self.parse_news_feed('https://www.animenewsnetwork.com/newsroom/rss.xml', limit), []

        for k, v in enumerate(data, start=1):
            embed = self.get_aninews_embed(v)
            embed.set_footer(text=f'{embed.footer.text} • Page {k}/{len(data)}')
            embeds.append(embed)

        view = NewsView(interaction=interaction, embeds=embeds)
        await interaction.followup.send(embed=embeds[0], view=view)

    @app_commands.command(name='crunchynews', description='Displays the latest anime news from Crunchyroll')
    @app_commands.describe(language='The language of the news', limit='The number of results to return')
    @app_commands.choices(
        language=[
            Choice(name='Arabic', value='arAR'),
            Choice(name='English', value='enEN'),
            Choice(name='French', value='frFR'),
            Choice(name='German', value='deDE'),
            Choice(name='Italian', value='itIT'),
            Choice(name='Portuguese', value='ptPT'),
            Choice(name='Russian', value='ruRU'),
            Choice(name='Spanish', value='esES'),
        ]
    )
    async def crunchynews_slash_command(
        self,
        interaction: discord.Interaction,
        language: Optional[Choice[str]] = None,
        limit: Optional[app_commands.Range[int, 1, 30]] = 15,
    ):
        await interaction.response.defer()

        data, embeds = (
            await self.parse_news_feed(
                f'https://www.crunchyroll.com/newsrss?lang={getattr(language, "value", "enEN")}', limit
            ),
            [],
        )

        for k, v in enumerate(data, start=1):
            embed = self.get_crunchynews_embed(v)
            embed.set_footer(text=f'{embed.footer.text} • Page {k}/{len(data)}')
            embeds.append(embed)

        view = NewsView(interaction=interaction, embeds=embeds)
        await interaction.followup.send(embed=embeds[0], view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(News(bot))
