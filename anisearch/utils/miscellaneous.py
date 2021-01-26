"""
This file is part of the AniSearch Discord Bot.

Copyright (C) 2021 IchBinLeoon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import time
from datetime import timedelta

import anisearch
from anisearch.bot import AniSearchBot

log = logging.getLogger(__name__)


def get_guild_count(bot: AniSearchBot) -> int:
    """Returns the bot guild count."""
    guilds = len(bot.guilds)
    return guilds


def get_user_count(bot: AniSearchBot) -> int:
    """Returns the bot user count."""
    users = 0
    for guild in bot.guilds:
        users += guild.member_count
    return users


def get_channel_count(bot: AniSearchBot) -> int:
    """Returns the bot channel count."""
    channels = 0
    for guild in bot.guilds:
        channels += len(guild.channels)
    return channels


def get_uptime(bot: AniSearchBot) -> timedelta:
    """Returns the bot uptime."""
    uptime = timedelta(seconds=round(time.time() - bot.start_time))
    return uptime


def get_version() -> str:
    """Returns the bot version."""
    version = anisearch.__version__
    return version


def get_creator() -> int:
    """Returns the discord id of the bot creator."""
    creator_id = 223871059068321793
    return creator_id


def get_bot() -> int:
    """Returns the discord id of the official bot instance."""
    bot_id = 737236600878137363
    return bot_id


def get_invite() -> str:
    """Returns the discord invite link for the bot."""
    invite = 'https://discord.com/oauth2/authorize?client_id=737236600878137363&permissions=124992&scope=bot'
    return invite


def get_vote() -> str:
    """Returns the top.gg vote link for the bot."""
    vote = 'https://top.gg/bot/737236600878137363/vote'
    return vote


def get_url() -> str:
    """Returns the github url for the source code of the bot."""
    url = anisearch.__url__
    return url
