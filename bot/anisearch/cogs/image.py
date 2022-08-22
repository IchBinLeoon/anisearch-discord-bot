import logging
from datetime import timedelta
from typing import List, Optional, Dict, Any

import discord
from discord import app_commands
from discord.ext import commands
from waifu import WaifuAioClient

from anisearch.bot import AniSearchBot
from anisearch.utils.checks import nsfw_embed_allowed
from anisearch.utils.menus import SimplePaginationView, BaseView

log = logging.getLogger(__name__)


class SearchImageView(SimplePaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class WaifuImageView(BaseView):
    def __init__(self, interaction: discord.Interaction, client: WaifuAioClient, image: str) -> None:
        super().__init__(interaction, timeout=60)
        self.client = client
        self.image = image

    @discord.ui.button(label='Roll', emoji='\N{GAME DIE}', style=discord.ButtonStyle.green)
    async def on_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        url = await self.client.sfw(self.image)
        embed = interaction.message.embeds[0].set_image(url=url)

        await interaction.followup.edit_message(interaction.message.id, embed=embed)

    @discord.ui.button(label='Cancel', emoji='\N{WASTEBASKET}', style=discord.ButtonStyle.red)
    async def on_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.close()


class Image(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @staticmethod
    def get_trace_embed(data: Dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(title=data.get('anilist').get('title').get('romaji'), color=0x4169E1)
        embed.set_image(url=data.get('image'))
        embed.set_footer(text=f'Provided by https://trace.moe/')

        embed.add_field(
            name='Episode',
            value=f'{data.get("episode")} ({timedelta(seconds=round(data.get("from")))})',
            inline=False,
        )

        embed.add_field(name='Similarity', value=f'{(data.get("similarity")) * 100:0.2f}%', inline=False)

        if data.get('anilist').get('id'):
            embed.add_field(
                name='AniList', value=f'https://anilist.co/anime/{data.get("anilist").get("id")}', inline=False
            )

        if data.get('anilist').get('idMal'):
            embed.add_field(
                name='MyAnimeList',
                value=f'https://myanimelist.net/anime/{data.get("anilist").get("idMal")}',
                inline=False,
            )

        return embed

    @app_commands.command(
        name='trace',
        description='Tries to find the anime the image is from through the image url or the image as attachment',
    )
    @app_commands.describe(url='Search by image url', attachment='Search by image as attachment')
    async def trace_slash_command(
        self,
        interaction: discord.Interaction,
        url: Optional[str] = None,
        attachment: Optional[discord.Attachment] = None,
    ):
        await interaction.response.defer()

        if url is None and attachment is None:
            embed = discord.Embed(title=f':no_entry: A url or attachment must be specified.', color=0x4169E1)
            return await interaction.followup.send(embed=embed)

        url = url or attachment.url

        if data := await self.bot.tracemoe.search(image=url, anilist_info=True):
            embeds = []

            for k, v in enumerate(data, start=1):
                if not nsfw_embed_allowed(interaction.channel, v.get('anilist').get('isAdult')):
                    continue

                embed = self.get_trace_embed(v)
                embed.set_footer(text=f'{embed.footer.text} • Page {k}/{len(data)}')
                embeds.append(embed)

            view = SearchImageView(interaction=interaction, embeds=embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(title=f':no_entry: An anime could not be found.', color=0x4169E1)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name='waifu', description='Posts a random image of a waifu')
    async def waifu_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw('waifu')

        embed = discord.Embed(title=':frame_photo: :sparkling_heart: Waifu', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image='waifu')
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='neko', description='Posts a random image of a catgirl')
    async def neko_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw('neko')

        embed = discord.Embed(title=':frame_photo: :cat: Neko', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image='neko')
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Image(bot))
