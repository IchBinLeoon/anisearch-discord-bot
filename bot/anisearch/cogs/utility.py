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
            description=f'**Avatar of {user.mention}**',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_image(url=user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        view = LinkView(label='Download Image', emoji='\N{INBOX TRAY}', url=str(user.display_avatar))
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='userinfo', description='Displays information about a server member')
    @app_commands.describe(member='The server member')
    async def userinfo_slash_command(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        user = member or interaction.user

        data = {
            'Name': user.name,
            'Nickname': user.display_name if user.display_name != user.name else '-',
            'Discriminator': user.discriminator,
            'Bot': user.bot,
            'Joined': discord.utils.format_dt(user.joined_at),
            'Created': discord.utils.format_dt(user.created_at),
            'ID': user.id,
        }

        info = '\n'.join([f'• {k}: **{v}**' for k, v in data.items()])

        embed = discord.Embed(
            title=':bust_in_silhouette: User Info',
            description=f'**Information about {user.mention}**\n\n{info}',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='serverinfo', description='Displays information about the current server')
    async def serverinfo_slash_command(self, interaction: discord.Interaction):
        guild = interaction.guild

        data = {
            'Name': guild.name,
            'Owner': f'<@!{guild.owner_id}>',
            'Members': guild.member_count,
            'Channels': len(guild.channels),
            'Roles': len(guild.roles),
            'Server Boosts': guild.premium_subscription_count,
            'Created': discord.utils.format_dt(guild.created_at),
            'ID': guild.id,
        }

        embed = discord.Embed(
            title=':shield: Server Info',
            description='\n'.join([f'• {k}: **{v}**' for k, v in data.items()]),
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Utility(bot))
