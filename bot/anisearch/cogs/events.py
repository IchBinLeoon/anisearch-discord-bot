import logging
import os
from asyncio import sleep
from typing import Any

import discord
import pysaucenao
import tracemoe
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.cogs.profile import MyAnimeListTimeout, MyAnimeListUnavailable
from anisearch.utils.http import post

log = logging.getLogger(__name__)

TOPGG_TOKEN = os.getenv('BOT_TOPGG_TOKEN')


def _get_full_class_name(obj: Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


class Events(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

        self.change_presence.start()

        if TOPGG_TOKEN:
            self.post_topgg_stats.start()

    @Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log.info(f'Bot joined guild {guild.id}')
        await self.bot.db.add_guild(guild.id)

    @Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        log.info(f'Bot left guild {guild.id}')
        await self.bot.db.remove_guild(guild.id)

    @Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            log.info(f'User {interaction.user.id} executed command {interaction.command.qualified_name}')
            await self.bot.db.add_user(interaction.user.id)

            if interaction.guild_id is None:
                await self.bot.db.add_private_command_usage(
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
                await self.bot.db.add_guild(interaction.guild_id)

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        exception = getattr(error, 'original', error)

        if isinstance(exception, app_commands.MissingPermissions):
            title = error

        elif isinstance(exception, MyAnimeListTimeout):
            title = 'Request to MyAnimeList timed out. Please try again in a moment.'
        elif isinstance(exception, MyAnimeListUnavailable):
            title = 'Failed to connect to MyAnimeList. Please try again in a moment.'

        elif isinstance(exception, tracemoe.BadRequest) or isinstance(exception, pysaucenao.InvalidImageException):
            title = 'Image is malformed or invalid.'

        else:
            title = 'An unknown error occurred. Please try again in a moment.'
            log.exception(error)

            embed = discord.Embed(
                title=f':x: {_get_full_class_name(exception)}', description=f'```{error}```', color=0xFF0000
            )
            embed.set_author(name='AniSearch Command Error', icon_url=self.bot.user.display_avatar)
            embed.add_field(name='Command', value=f'`{interaction.command.qualified_name}`', inline=False)

            if interaction.data.get('options'):
                if interaction.command.parent:
                    if values := interaction.data.get('options')[0].get('options'):
                        options = [f'`{i.get("name")}: {i.get("value")}`' for i in values]
                    else:
                        options = None
                else:
                    options = [f'`{i.get("name")}: {i.get("value")}`' for i in interaction.data.get('options')]

                if options:
                    embed.add_field(name='Options', value=', '.join(options), inline=False)

            await (await self.bot.application_info()).owner.send(embed=embed)

        embed = discord.Embed(title=f':x: {title}', color=0xFF0000, timestamp=discord.utils.utcnow())
        embed.set_author(name='AniSearch Error', icon_url=self.bot.user.display_avatar)
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar)

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

    @tasks.loop(seconds=80)
    async def change_presence(self) -> None:
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name='/help'), status=discord.Status.online
        )
        await sleep(20)
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name=f'on {len(self.bot.guilds)} servers'),
            status=discord.Status.online,
        )
        await sleep(20)
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, name=f'with {sum([i.member_count for i in self.bot.guilds])} users'
            ),
            status=discord.Status.online,
        )
        await sleep(20)
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name='Anime'), status=discord.Status.online
        )

    @change_presence.before_loop
    async def change_presence_before(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def post_topgg_stats(self) -> None:
        log.info(f'Posting TopGG statistics')

        try:
            guilds = len(self.bot.guilds)
            shards = self.bot.shard_count

            await post(
                url=f'https://top.gg/api/bots/{self.bot.user.id}/stats',
                session=self.bot.session,
                res_method='json',
                json={'server_count': guilds, 'shard_count': shards},
                headers={'Authorization': TOPGG_TOKEN},
            )

            log.info(f'TopGG statistics posted (Guilds: {guilds}, Shards: {shards})')

        except Exception as e:
            log.error(f'Error while posting TopGG statistics: {e}')

    @post_topgg_stats.before_loop
    async def post_topgg_stats_before(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Events(bot))
