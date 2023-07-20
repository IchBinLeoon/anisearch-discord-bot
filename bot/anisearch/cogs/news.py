import html
import logging
from typing import List, Dict, Any, Optional

import discord
from bs4 import BeautifulSoup
from discord import app_commands
from discord.app_commands import Choice
from discord.ext.commands import Cog

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


class News(Cog):
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

    @app_commands.command(name='aninews', description='Displays the latest anime news from Anime News Network')
    @app_commands.describe(limit='The number of results to return')
    async def aninews_slash_command(
        self, interaction: discord.Interaction, limit: Optional[app_commands.Range[int, 1, 30]] = 15
    ):
        await interaction.response.defer()

        data, embeds = await self.parse_news_feed('https://www.animenewsnetwork.com/newsroom/rss.xml', limit), []

        for page, news in enumerate(data, start=1):
            embed = discord.Embed(
                title=news.get('title'),
                description=f'```{html.unescape(clean_html(news.get("description")))}```',
                color=0x4169E1,
                url=news.get('link'),
            )

            name = f'Anime News Network • {news.get("date").replace("-0500", "EST")}'
            if news.get('category'):
                name += f' • {news.get("category")}'

            embed.set_author(name=name, icon_url=ANIMENEWSNETWORK_LOGO)
            embed.set_footer(text=f'Provided by https://www.animenewsnetwork.com/ • Page {page}/{len(data)}')

            embeds.append(embed)

        view = NewsView(interaction=interaction, embeds=embeds)
        await interaction.followup.send(embed=embeds[0], view=view)

    @app_commands.command(name='crunchynews', description='Displays the latest anime news from Crunchyroll')
    @app_commands.describe(language='The language of the news', limit='The number of results to return')
    @app_commands.choices(
        language=[
            Choice(name='Arabic', value='ar-SA'),
            Choice(name='English', value='en-US'),
            Choice(name='French', value='fr-FR'),
            Choice(name='German', value='de-DE'),
            Choice(name='Italian', value='it-IT'),
            Choice(name='Portuguese', value='pt-PT'),
            Choice(name='Russian', value='ru-RU'),
            Choice(name='Spanish', value='es-ES'),
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
                f'https://cr-news-api-service.prd.crunchyrollsvc.com/v1/{getattr(language, "value", "en-US")}/rss',
                limit,
            ),
            [],
        )

        for page, news in enumerate(data, start=1):
            embed = discord.Embed(
                title=news.get('title'),
                description=f'```{html.unescape(clean_html(news.get("description")))}```',
                color=0x4169E1,
                url=news.get('link'),
            )
            embed.set_author(name=f'Crunchyroll • {news.get("date")}', icon_url=CRUNCHYROLL_LOGO)
            embed.set_footer(text=f'Provided by https://www.crunchyroll.com/ • Page {page}/{len(data)}')

            embeds.append(embed)

        view = NewsView(interaction=interaction, embeds=embeds)
        await interaction.followup.send(embed=embeds[0], view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(News(bot))
