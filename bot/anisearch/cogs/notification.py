import asyncio
import logging
from typing import List, Dict, Any, Callable

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Cog

from anisearch.bot import AniSearchBot
from anisearch.cogs.profile import ANILIST_LOGO
from anisearch.utils.formatters import format_media_title
from anisearch.utils.menus import SimplePaginationView

log = logging.getLogger(__name__)


class NotificationTimer:
    def __init__(self, timer_id: int, timeout: int, callback: Callable, data: Dict[str, Any]) -> None:
        self._timer_id = timer_id
        self._timeout = timeout
        self._callback = callback
        self._data = data
        self._task = asyncio.ensure_future(self._job())

    @property
    def id(self) -> int:
        return self._timer_id

    async def _job(self) -> None:
        await asyncio.sleep(self._timeout)
        await self._callback(self, self._data)

    def cancel(self) -> None:
        if not self._task.cancelled():
            self._task.cancel()

    def is_done(self) -> bool:
        return self._task.done()


class NotificationListView(SimplePaginationView):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]) -> None:
        super().__init__(interaction, embeds, timeout=180)


class NotificationView(discord.ui.View):
    def __init__(self, urls: Dict[str, str]) -> None:
        super().__init__()

        for k, v in urls.items():
            self.add_item(discord.ui.Button(label=k, url=v))


class Notification(Cog):
    def __init__(self, bot: AniSearchBot) -> None:
        self.bot = bot
        self._timers = []

        self.fetch_episode_schedule.start()

    @tasks.loop(minutes=30)
    async def fetch_episode_schedule(self) -> None:
        log.info('Fetching episode schedule')

        try:
            data = await self.bot.anilist.schedule(page=1, perPage=50, notYetAired=True, sort='TIME')

            for i in data:
                if i.get('media').get('isAdult') or i.get('media').get('countryOfOrigin') != 'JP':
                    continue

                timer_id = i.get('id')

                if not any(t.id == timer_id for t in self._timers):
                    timeout = i.get('timeUntilAiring') + 15

                    timer = NotificationTimer(timer_id, timeout, self.send_episode_notification, i)

                    self._timers.append(timer)

            log.info(f'Episode schedule fetched (Timers: {len(self._timers)})')

        except Exception as e:
            log.error(f'Error while fetching episode schedule: {e}')

    @fetch_episode_schedule.before_loop
    async def fetch_episode_schedule_before(self) -> None:
        await self.bot.wait_until_ready()

    async def send_episode_notification(self, timer: NotificationTimer, data: Dict[str, Any]) -> None:
        log.info(f'Sending episode notification (Timer: {timer.id}, Anime: {data.get("media").get("id")})')
        self._timers.remove(timer)

        counter = 0

        for i in await self.bot.db.get_notification_channels(data.get('media').get('id')):
            channel = self.bot.get_channel(i.get('channel_id'))

            role = self.bot.get_guild(i.get('guild_id')).get_role(i.get('role_id'))

            if channel:
                embed = discord.Embed(
                    title=format_media_title(
                        data.get('media').get('title').get('romaji'), data.get('media').get('title').get('english')
                    ),
                    description=f'Episode **{data.get("episode")}** is out!',
                    url=data.get('media').get('siteUrl'),
                    color=0x4169E1,
                )
                embed.set_author(name='Episode Notification', icon_url=ANILIST_LOGO)
                embed.set_footer(text='Provided by https://anilist.co/')

                if data.get('media').get('coverImage').get('large'):
                    embed.set_image(url=data.get('media').get('coverImage').get('large'))

                urls = {'AniList': data.get('media').get('siteUrl')}

                if mal := data.get('media').get('idMal'):
                    urls['MyAnimeList'] = f'https://myanimelist.net/anime/{mal}'

                view = NotificationView(urls=urls)

                try:
                    if role:
                        await channel.send(content=role.mention, embed=embed, view=view)
                    else:
                        await channel.send(embed=embed, view=view)

                    counter += 1
                except discord.Forbidden:
                    pass
                except Exception as e:
                    log.error(f'Error while sending episode notification (Channel: {channel.id}): {e}')

        try:
            if data.get('episode') == data.get('media').get('episodes'):
                await self.bot.db.remove_episode_notifications(data.get('media').get('id'))
        except Exception as e:
            log.warning(f'Error while removing episode notifications: {e}')

        log.info(f'Sent episode notification (Channels: {counter})')

    notification_group = app_commands.Group(
        name='notification', description='Episode notification management commands', guild_only=True
    )

    @notification_group.command(
        name='add',
        description='Adds an anime to your server notification list',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_add_slash_command(self, interaction: discord.Interaction, anilist_id: int):
        await interaction.response.defer()

        if not await self.bot.db.get_guild_channel(interaction.guild_id):
            embed = discord.Embed(
                title=f':warning: It is recommended to set a channel before adding anime to the server notification list.',
                color=0x4169E1,
            )
            await interaction.followup.send(embed=embed)

        if await self.bot.db.get_guild_episode_notification(interaction.guild_id, anilist_id):
            embed = discord.Embed(
                title=f':no_entry: The ID `{anilist_id}` is already on the server notification list.',
                color=0x4169E1,
            )
            return await interaction.followup.send(embed=embed)

        if data := await self.bot.anilist.media(
            page=1, perPage=1, id=anilist_id, type='ANIME', isAdult=False, countryOfOrigin='JP'
        ):
            await self.bot.db.add_guild_episode_notification(
                interaction.guild_id, data[0].get('id'), data[0].get('title').get('romaji'), interaction.user.id
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

    @notification_group.command(
        name='remove',
        description='Removes an anime from your server notification list',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.describe(anilist_id='The AniList ID of the anime')
    @app_commands.rename(anilist_id='id')
    @app_commands.checks.has_permissions(manage_guild=True)
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

    @notification_group.command(
        name='list',
        description='Displays your server notification list',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_list_slash_command(self, interaction: discord.Interaction):
        if anime := await self.bot.db.get_guild_episode_notifications(interaction.guild_id):
            entries, embeds = [anime[i : i + 5] for i in range(0, len(anime), 5)], []

            for page, values in enumerate(entries, start=1):
                embed = discord.Embed(title='Notification List', color=0x4169E1)
                embed.set_thumbnail(url=interaction.guild.icon)
                embed.set_footer(text=f'Page {page}/{len(entries)}')

                for i in values:
                    anilist_id = f'**{i.get("anilist_id")}**'
                    added_by = f'<@{i.get("added_by")}>'
                    added_at = discord.utils.format_dt(i.get('added_at'), 'R')

                    embed.add_field(
                        name=i.get('title'),
                        value=f'AniList ID: {anilist_id}\nAdded By: {added_by}\nAdded At: {added_at}',
                        inline=False,
                    )

                embeds.append(embed)

            view = NotificationListView(interaction=interaction, embeds=embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)
        else:
            embed = discord.Embed(title=f':no_entry: No anime added to the server notification list.', color=0x4169E1)
            await interaction.response.send_message(embed=embed)

    @notification_group.command(
        name='clear',
        description='Removes all anime from your server notification list',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_clear_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_episode_notifications(interaction.guild_id):
            await self.bot.db.remove_guild_episode_notifications(interaction.guild_id)

            embed = discord.Embed(
                title=f':white_check_mark: Removed all anime from the server notification list.', color=0x4169E1
            )
        else:
            embed = discord.Embed(title=f':no_entry: No anime added to the server notification list.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)

    @notification_group.command(
        name='setchannel',
        description='Sets the channel for episode notifications',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.describe(channel='The text channel')
    @app_commands.checks.has_permissions(manage_guild=True)
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

    @notification_group.command(
        name='removechannel', description='Removes the set channel', extras={'Required Permissions': 'Manage Server'}
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_removechannel_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_channel(interaction.guild_id):
            await self.bot.db.remove_guild_channel(interaction.guild_id)

            embed = discord.Embed(title=f':white_check_mark: The set channel has been removed.', color=0x4169E1)
        else:
            embed = discord.Embed(title=f':no_entry: You have not set a channel.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)

    @notification_group.command(
        name='setrole',
        description='Sets the role for episode notification pings',
        extras={'Required Permissions': 'Manage Server'},
    )
    @app_commands.describe(role='The role')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_setrole_slash_command(self, interaction: discord.Interaction, role: discord.Role):
        await self.bot.db.add_guild_role(interaction.guild_id, role.id)

        embed = discord.Embed(
            title=':white_check_mark: Notification Role',
            description=f'**Set the notification role to {role.mention}**',
            color=0x4169E1,
        )
        await interaction.response.send_message(embed=embed)

    @notification_group.command(
        name='removerole', description='Removes the set role', extras={'Required Permissions': 'Manage Server'}
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notification_removerole_slash_command(self, interaction: discord.Interaction):
        if await self.bot.db.get_guild_role(interaction.guild_id):
            await self.bot.db.remove_guild_role(interaction.guild_id)

            embed = discord.Embed(title=f':white_check_mark: The set role has been removed.', color=0x4169E1)
        else:
            embed = discord.Embed(title=f':no_entry: You have not set a role.', color=0x4169E1)

        await interaction.response.send_message(embed=embed)


async def setup(bot: AniSearchBot) -> None:
    await bot.add_cog(Notification(bot))
