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
    @app_commands.guild_only()
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

    @app_commands.command(name='userinfo', description='Displays information about a server member')
    @app_commands.describe(member='The server member')
    @app_commands.guild_only()
    async def userinfo_slash_command(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        user = member or interaction.user

        embed = discord.Embed(
            title=':bust_in_silhouette: User Info',
            description=f'Information about {user.mention}',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Name', value=user.name, inline=True)
        embed.add_field(name='❯ Nickname', value=user.nick or '-', inline=True)
        embed.add_field(name='❯ Discriminator', value=user.discriminator, inline=True)
        embed.add_field(name='❯ Created', value=discord.utils.format_dt(user.created_at, 'R'), inline=True)
        embed.add_field(name='❯ Joined', value=discord.utils.format_dt(user.joined_at, 'R'), inline=True)
        embed.add_field(name='❯ Bot', value=user.bot, inline=True)
        embed.add_field(name='❯ Avatar', value=f'[Click Here]({user.display_avatar.url})', inline=True)
        embed.add_field(name='❯ Top Role', value=user.top_role.mention, inline=True)

        commands_used = await self.bot.db.get_user_command_usages_count(user.id)
        embed.add_field(name='❯ Commands Used', value=commands_used, inline=True)

        embed.add_field(name='❯ ID', value=user.id, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='serverinfo', description='Displays information about the current server')
    @app_commands.guild_only()
    async def serverinfo_slash_command(self, interaction: discord.Interaction):
        guild = interaction.guild

        embed = discord.Embed(
            title=':shield: Server Info',
            description='Information about this server',
            color=0x4169E1,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        embed.add_field(name='❯ Name', value=guild.name, inline=True)
        embed.add_field(name='❯ Owner', value=f'<@!{guild.owner_id}>', inline=True)
        embed.add_field(name='❯ Locale', value=guild.preferred_locale, inline=True)
        embed.add_field(name='❯ Members', value=guild.member_count, inline=True)
        embed.add_field(name='❯ Channels', value=len(guild.channels), inline=True)
        embed.add_field(name='❯ Roles', value=len(guild.roles), inline=True)
        embed.add_field(name='❯ Created', value=discord.utils.format_dt(guild.created_at, 'R'), inline=True)
        embed.add_field(name='❯ Server Boosts', value=guild.premium_subscription_count, inline=True)

        commands_used = await self.bot.db.get_guild_command_usages_count(guild.id)
        embed.add_field(name='❯ Commands Used', value=commands_used, inline=True)

        embed.add_field(name='❯ ID', value=guild.id, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Utility(bot))
