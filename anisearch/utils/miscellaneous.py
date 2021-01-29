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

import anisearch
from anisearch.utils.constants import DISCORD_INVITE, CREATOR_ID, BOT_ID, TOPGG_VOTE

log = logging.getLogger(__name__)


def get_version() -> str:
    """
    Returns the bot version.
    """
    version = anisearch.__version__
    return version


def get_creator() -> int:
    """
    Returns the discord id of the bot creator.
    """
    creator_id = CREATOR_ID
    return creator_id


def get_bot() -> int:
    """
    Returns the discord id of the official bot instance.
    """
    bot_id = BOT_ID
    return bot_id


def get_invite() -> str:
    """
    Returns the discord invite link for the bot.
    """
    invite = DISCORD_INVITE
    return invite


def get_vote() -> str:
    """
    Returns the top.gg vote link for the bot.
    """
    vote = TOPGG_VOTE
    return vote


def get_url() -> str:
    """
    Returns the github url for the source code of the bot.
    """
    url = anisearch.__url__
    return url
