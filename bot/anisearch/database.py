import logging
from typing import List

import asyncpg

log = logging.getLogger(__name__)


async def create_postgres_pool(database_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=database_url, min_size=10, max_size=100)


class Database:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def close(self) -> None:
        await self.pool.close()

    async def add_guild(self, guild_id: int) -> None:
        await self.pool.execute('INSERT INTO guilds (id) VALUES ($1) ON CONFLICT (id) DO NOTHING', guild_id)

    async def remove_guild(self, guild_id: int) -> None:
        await self.pool.execute('DELETE FROM guilds WHERE id = $1', guild_id)

    async def add_user(self, user_id: int) -> None:
        await self.pool.execute('INSERT INTO users (id) VALUES ($1) ON CONFLICT (id) DO NOTHING', user_id)

    async def add_user_profile(self, user_id: int, platform: str, profile_id: int) -> None:
        await self.pool.execute(
            "INSERT INTO user_profiles (user_id, platform, profile_id) VALUES ($1, $2, $3) ON CONFLICT (user_id, platform) DO UPDATE SET profile_id = $3, added_at = current_timestamp",
            user_id,
            platform,
            profile_id,
        )

    async def remove_user_profile(self, user_id: int, platform: str) -> None:
        await self.pool.execute("DELETE FROM user_profiles WHERE user_id = $1 AND platform = $2", user_id, platform)

    async def get_user_profile(self, user_id: int, platform: str) -> asyncpg.Record:
        return await self.pool.fetchrow(
            "SELECT * FROM user_profiles WHERE user_id = $1 AND platform = $2", user_id, platform
        )

    async def get_notification_channels(self, anilist_id: int) -> List[asyncpg.Record]:
        return await self.pool.fetch(
            'SELECT guild_channels.guild_id, guild_channels.channel_id, guild_roles.role_id FROM guild_channels LEFT JOIN guild_roles ON guild_channels.guild_id = guild_roles.guild_id LEFT JOIN guild_episode_notifications ON guild_channels.guild_id = guild_episode_notifications.guild_id WHERE guild_episode_notifications.guild_id IS NULL OR guild_episode_notifications.anilist_id = $1',
            anilist_id,
        )

    async def add_guild_episode_notification(self, guild_id: int, anilist_id: int, title: str, added_by: int) -> None:
        await self.pool.execute(
            'INSERT INTO guild_episode_notifications (guild_id, anilist_id, title, added_by) VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, anilist_id) DO NOTHING',
            guild_id,
            anilist_id,
            title,
            added_by,
        )

    async def remove_guild_episode_notification(self, guild_id: int, anilist_id: int) -> None:
        await self.pool.execute(
            'DELETE FROM guild_episode_notifications WHERE guild_id = $1 AND anilist_id = $2', guild_id, anilist_id
        )

    async def get_guild_episode_notification(self, guild_id: int, anilist_id: int) -> asyncpg.Record:
        return await self.pool.fetchrow(
            'SELECT * FROM guild_episode_notifications WHERE guild_id = $1 AND anilist_id = $2', guild_id, anilist_id
        )

    async def remove_guild_episode_notifications(self, guild_id: int) -> None:
        await self.pool.execute('DELETE FROM guild_episode_notifications WHERE guild_id = $1', guild_id)

    async def get_guild_episode_notifications(self, guild_id: int) -> List[asyncpg.Record]:
        return await self.pool.fetch('SELECT * FROM guild_episode_notifications WHERE guild_id = $1', guild_id)

    async def remove_episode_notifications(self, anilist_id: int) -> None:
        await self.pool.execute('DELETE FROM guild_episode_notifications WHERE anilist_id = $1', anilist_id)

    async def add_guild_channel(self, guild_id: int, channel_id: int) -> None:
        await self.pool.execute(
            'INSERT INTO guild_channels (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2, added_at = current_timestamp',
            guild_id,
            channel_id,
        )

    async def remove_guild_channel(self, guild_id: int) -> None:
        await self.pool.execute('DELETE FROM guild_channels WHERE guild_id = $1', guild_id)

    async def get_guild_channel(self, guild_id: int) -> asyncpg.Record:
        return await self.pool.fetchrow('SELECT * FROM guild_channels WHERE guild_id = $1', guild_id)

    async def add_guild_role(self, guild_id: int, role_id: int) -> None:
        await self.pool.execute(
            'INSERT INTO guild_roles (guild_id, role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET role_id = $2, added_at = current_timestamp',
            guild_id,
            role_id,
        )

    async def remove_guild_role(self, guild_id: int) -> None:
        await self.pool.execute('DELETE FROM guild_roles WHERE guild_id = $1', guild_id)

    async def get_guild_role(self, guild_id: int) -> asyncpg.Record:
        return await self.pool.fetchrow('SELECT * FROM guild_roles WHERE guild_id = $1', guild_id)

    async def add_guild_command_usage(
        self,
        shard_id: int,
        guild_id: int,
        channel_id: int,
        user_id: int,
        command_name: str,
        command_type: str,
    ) -> None:
        await self.pool.execute(
            'INSERT INTO guild_command_usages (shard_id, guild_id, channel_id, user_id, command_name, command_type) VALUES ($1, $2, $3, $4, $5, $6)',
            shard_id,
            guild_id,
            channel_id,
            user_id,
            command_name,
            command_type,
        )

    async def add_private_command_usage(self, user_id: int, command_name: str, command_type: str) -> None:
        await self.pool.execute(
            'INSERT INTO private_command_usages (user_id, command_name, command_type) VALUES ($1, $2, $3)',
            user_id,
            command_name,
            command_type,
        )

    async def get_guild_command_usages_count(self, guild_id: int) -> int:
        return await self.pool.fetchval('SELECT COUNT(*) FROM guild_command_usages WHERE guild_id = $1', guild_id)

    async def get_user_command_usages_count(self, user_id: int) -> int:
        return await self.pool.fetchval(
            'SELECT (SELECT COUNT(*) FROM guild_command_usages WHERE user_id = $1) + (SELECT COUNT(*) FROM private_command_usages WHERE user_id = $1)',
            user_id,
        )

    async def get_global_command_usages_count(self, command_name: str) -> int:
        return await self.pool.fetchval(
            'SELECT (SELECT COUNT(*) FROM guild_command_usages WHERE command_name = $1) + (SELECT COUNT(*) FROM private_command_usages WHERE command_name = $1)',
            command_name,
        )
