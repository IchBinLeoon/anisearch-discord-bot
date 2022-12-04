import logging

import discord
from discord import app_commands
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


class Notification(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot

    notification_group = app_commands.Group(
        name='notification', description='Episode notification management commands', guild_only=True
    )

    @notification_group.command(name='add', description='Adds an anime to your server notification list')
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_add_slash_command(self, interaction: discord.Interaction, anilist_id: int):
        await interaction.response.defer()

        await interaction.followup.send('notification add')

    @notification_group.command(name='remove', description='Removes an anime from your server notification list')
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_remove_slash_command(self, interaction: discord.Interaction, anilist_id: int):
        await interaction.response.send_message('notification remove')

    @notification_group.command(name='list', description='Displays your server notification list')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_list_slash_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await interaction.followup.send('notification list')

    @notification_group.command(name='clear', description='Removes all anime from your server notification list')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_clear_slash_command(self, interaction: discord.Interaction):
        await interaction.response.send_message('notification clear')

    @notification_group.command(name='setchannel', description='Sets the channel for episode notifications')
    @app_commands.describe(channel='The text channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_setchannel_slash_command(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await self.bot.db.add_guild_channel(interaction.guild_id, channel.id)

        embed = discord.Embed(
            title=':white_check_mark: Notification Channel',
            description=f'Set the notification channel to {channel.mention}',
            color=0x4169E1,
        )
        await interaction.response.send_message(embed=embed)

    @notification_group.command(name='removechannel', description='Removes the set channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_removechannel_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_channel(interaction.guild_id):
            await self.bot.db.remove_guild_channel(interaction.guild_id)

            embed = discord.Embed(title=f':white_check_mark: The set channel has been removed.', color=0x4169E1)
        else:
            embed = discord.Embed(title=f':no_entry: You have not set a channel.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)

    @notification_group.command(name='setrole', description='Sets the role for episode notification pings')
    @app_commands.describe(role='The role')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_setrole_slash_command(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message('notification setrole')

    @notification_group.command(name='removerole', description='Removes the set role')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_removerole_slash_command(self, interaction: discord.Interaction):
        await interaction.response.send_message('notification removerole')


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Notification(bot))
