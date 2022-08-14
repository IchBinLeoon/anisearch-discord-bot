from typing import Any

import discord


def is_private_channel(channel: Any) -> bool:
    return channel.type == discord.ChannelType.private


def nsfw_embed_allowed(channel: Any, is_adult: bool) -> bool:
    if is_private_channel(channel):
        return True

    if not is_adult:
        return True

    if is_adult and channel.is_nsfw():
        return True

    return False
