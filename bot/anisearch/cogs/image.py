import logging

import discord
from discord import app_commands
from discord.ext import commands
from waifu import WaifuAioClient

from anisearch.bot import AniSearchBot
from anisearch.utils.menus import BaseView

log = logging.getLogger(__name__)


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

    @app_commands.command(name='waifu', description='Posts a random image of a waifu')
    async def waifu_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw(interaction.command.qualified_name)

        embed = discord.Embed(title=':frame_photo: :sparkling_heart: Waifu', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image=interaction.command.qualified_name)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='neko', description='Posts a random image of a catgirl')
    async def neko_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw(interaction.command.qualified_name)

        embed = discord.Embed(title=':frame_photo: :cat: Neko', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image=interaction.command.qualified_name)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='shinobu', description='Posts a random image of shinobu')
    async def shinobu_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw(interaction.command.qualified_name)

        embed = discord.Embed(title=':frame_photo: :doughnut: Shinobu', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image=interaction.command.qualified_name)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='megumin', description='Posts a random image of megumin')
    async def megumin_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = await self.bot.waifu.sfw(interaction.command.qualified_name)

        embed = discord.Embed(title=':frame_photo: :boom: Megumin', color=0x4169E1)
        embed.set_image(url=url)
        embed.set_footer(text='Provided by https://waifu.pics/')

        view = WaifuImageView(interaction=interaction, client=self.bot.waifu, image=interaction.command.qualified_name)
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Image(bot))
