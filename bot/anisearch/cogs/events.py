import logging
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


def _get_full_class_name(obj: Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


class Events(commands.Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log.info(f'Bot joined guild {guild.id}')
        await self.bot.db.add_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        log.info(f'Bot left guild {guild.id}')
        await self.bot.db.remove_guild(guild.id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            log.info(f'User {interaction.user.id} executed command {interaction.command.qualified_name}')

            if interaction.guild_id is None:
                await self.bot.db.add_dm_command_usage(
                    interaction.user.id,
                    interaction.command.qualified_name,
                    discord.AppCommandType(interaction.data.get('type')).name,
                )
            else:
                await self.bot.db.add_guild_command_usage(
                    interaction.guild.shard_id,
                    interaction.guild_id,
                    interaction.channel_id,
                    interaction.user.id,
                    interaction.command.qualified_name,
                    discord.AppCommandType(interaction.data.get('type')).name,
                )

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        exception = getattr(error, 'original', error)

        if isinstance(exception, app_commands.BotMissingPermissions):
            title = error

        else:
            title = 'An unknown error occurred.'
            log.error(error)

            embed = discord.Embed(
                title=f':x: {_get_full_class_name(exception)}', description=f'```{error}```', color=0xFF0000
            )
            embed.set_author(name='AniSearch Command Error', icon_url=self.bot.user.display_avatar)
            embed.add_field(name='Command', value=f'`{interaction.command.qualified_name}`', inline=False)

            if interaction.data.get('options'):
                options = ', '.join([f'`{i.get("name")}: {i.get("value")}`' for i in interaction.data.get('options')])
                embed.add_field(name='Options', value=options, inline=False)

            await (await self.bot.application_info()).owner.send(embed=embed)

        embed = discord.Embed(title=f':x: {title}', color=0xFF0000, timestamp=discord.utils.utcnow())
        embed.set_author(name='AniSearch Error', icon_url=self.bot.user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Events(bot))
