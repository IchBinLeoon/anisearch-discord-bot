import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from anisearch.bot import AniSearchBot
from anisearch.cogs.help import LinkView

log = logging.getLogger(__name__)


class Utility(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    @app_commands.command(name='avatar', description='Displays the avatar of a server member')
    @app_commands.describe(member='The server member')
    async def avatar_slash_command(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        user = member or interaction.user

        embed = discord.Embed(
            title=':frame_photo: Avatar',
            description=f'Avatar of {user.mention}',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_image(url=user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Download Image', emoji='\N{INBOX TRAY}', url=str(user.display_avatar))
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Utility(bot))
