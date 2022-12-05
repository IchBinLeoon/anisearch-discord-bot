import asyncio
import logging
import time
from typing import List, Dict, Any, Callable

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.utils.menus import SimplePaginationView

log = logging.getLogger(__name__)


class NotificationTimer:
    def __init__(self, timer_id: int, timeout: int, callback: Callable, data: Dict[str, Any]) -> None:
        self.timer_id = timer_id
        self._timeout = timeout
        self._callback = callback
        self._data = data
        self._task = asyncio.ensure_future(self._job())

    async def _job(self) -> None:
        await asyncio.sleep(self._timeout)
        await self._callback(self, self._data)

    def cancel(self) -> None:
        self._task.cancel()


class NotificationListView(SimplePaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class Notification(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot
        self._timers = []

        self.fetch_episode_schedule.start()

    @tasks.loop(hours=1)
    async def fetch_episode_schedule(self) -> None:
        log.info('Fetching episode schedule')

        data = await self.bot.anilist.schedule(page=1, perPage=50, notYetAired=True, sort='TIME')

        for i in data:
            if i.get('media').get('isAdult'):
                continue

            timer_id = int(str(i.get('media').get('id')) + str(i.get('airingAt')) + str(i.get('episode')))

            if not any(t.timer_id == timer_id for t in self._timers):
                timeout = int(i.get('airingAt') - time.time()) + 15

                timer = NotificationTimer(timer_id, timeout, self.send_episode_notification, i)

                self._timers.append(timer)

        log.info(f'Episode schedule fetched (Timers: {len(self._timers)})')

    @fetch_episode_schedule.before_loop
    async def fetch_episode_schedule_before(self) -> None:
        await self.bot.wait_until_ready()

    async def send_episode_notification(self, timer: NotificationTimer, data: Dict[str, Any]) -> None:
        log.info(
            f'New episode notification: {data.get("media").get("title").get("romaji")} ({data.get("media").get("id")})'
        )

        self._timers.remove(timer)

    notification_group = app_commands.Group(
        name='notification', description='Episode notification management commands', guild_only=True
    )

    @notification_group.command(name='add', description='Adds an anime to your server notification list')
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_add_slash_command(self, interaction: discord.Interaction, anilist_id: int):
        await interaction.response.defer()

        if await self.bot.db.get_guild_episode_notification(interaction.guild_id, anilist_id):
            embed = discord.Embed(
                title=f':no_entry: The ID `{anilist_id}` is already on the server notification list.',
                color=0x4169E1,
            )
            return await interaction.followup.send(embed=embed)

        if data := await self.bot.anilist.media(page=1, perPage=1, id=anilist_id, type='ANIME', isAdult=False):
            await self.bot.db.add_guild_episode_notification(
                interaction.guild_id, data[0].get('id'), data[0].get('title').get('romaji')
            )

            embed = discord.Embed(
                title=f':white_check_mark: Added `{data[0].get("title").get("romaji")}` to the server notification list.',
                color=0x4169E1,
            )
        else:
            embed = discord.Embed(
                title=f':no_entry: An anime with the ID `{anilist_id}` could not be found.', color=0x4169E1
            )

        await interaction.followup.send(embed=embed)

    @notification_group.command(name='remove', description='Removes an anime from your server notification list')
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_remove_slash_command(self, interaction: discord.Interaction, anilist_id: int):
        if await self.bot.db.get_guild_episode_notification(interaction.guild_id, anilist_id):
            await self.bot.db.remove_guild_episode_notification(interaction.guild_id, anilist_id)

            embed = discord.Embed(
                title=f':white_check_mark: Removed ID `{anilist_id}` from the server notification list.',
                color=0x4169E1,
            )
        else:
            embed = discord.Embed(
                title=f':no_entry: The ID `{anilist_id}` is not on the server notification list.', color=0x4169E1
            )

        await interaction.response.send_message(embed=embed)

    @notification_group.command(name='list', description='Displays your server notification list')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_list_slash_command(self, interaction: discord.Interaction):
        if anime := await self.bot.db.get_guild_episode_notifications(interaction.guild_id):
            entries, embeds = [anime[i : i + 5] for i in range(0, len(anime), 5)], []

            for page, values in enumerate(entries, start=1):
                embed = discord.Embed(title='Notification List', color=0x4169E1)
                embed.set_thumbnail(url=interaction.guild.icon)
                embed.set_footer(text=f'Page {page}/{len(entries)}')

                for i in values:
                    embed.add_field(
                        name=i.get('title'),
                        value=f'ID: {i.get("anilist_id")}\nAdded: {discord.utils.format_dt(i.get("added_at"), "R")}',
                        inline=False,
                    )

                embeds.append(embed)

            view = NotificationListView(interaction=interaction, embeds=embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(title=f':no_entry: No anime added to the server notification list.', color=0x4169E1)
            await interaction.response.send_message(embed=embed)

    @notification_group.command(name='clear', description='Removes all anime from your server notification list')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_clear_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_episode_notifications(interaction.guild_id):
            await self.bot.db.remove_guild_episode_notifications(interaction.guild_id)

            embed = discord.Embed(
                title=f':white_check_mark: Removed all anime from the server notification list.', color=0x4169E1
            )
        else:
            embed = discord.Embed(title=f':no_entry: No anime added to the server notification list.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)

    @notification_group.command(name='setchannel', description='Sets the channel for episode notifications')
    @app_commands.describe(channel='The text channel')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_setchannel_slash_command(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await self.bot.db.add_guild_channel(interaction.guild_id, channel.id)

        embed = discord.Embed(
            title=':white_check_mark: Notification Channel',
            description=f'**Set the notification channel to {channel.mention}**\n\nYou will receive a notification for each new episode as long as no specific anime has been added to the server list.',
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
        await self.bot.db.add_guild_role(interaction.guild_id, role.id)

        embed = discord.Embed(
            title=':white_check_mark: Notification Role',
            description=f'**Set the notification role to {role.mention}**',
            color=0x4169E1,
        )
        await interaction.response.send_message(embed=embed)

    @notification_group.command(name='removerole', description='Removes the set role')
    @app_commands.checks.has_permissions(administrator=True)
    async def notification_removerole_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_role(interaction.guild_id):
            await self.bot.db.remove_guild_role(interaction.guild_id)

            embed = discord.Embed(title=f':white_check_mark: The set role has been removed.', color=0x4169E1)
        else:
            embed = discord.Embed(title=f':no_entry: You have not set a role.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Notification(bot))
