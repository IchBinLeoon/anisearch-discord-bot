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
import random as rnd
from typing import Union

from discord.ext.commands import Context

logger = logging.getLogger(__name__)


def get_command_example(ctx: Context, command: str) -> Union[str, None]:
    """
    Returns an example of the specified command.

    Args:
        ctx (Context): The context in which the command was invoked under.
        command (str): The specified command.

    Returns:
        str: The command example.
    """
    anime = [
        'Sword Art Online',
        'Shingeki no Kyojin',
        'Death Note',
        'Steins;Gate'
    ]

    manga = [
        'Shingeki no Kyojin',
        'One Piece',
        'Tokyo Ghoul',
        'Jujutsu Kaisen'
    ]

    character = [
        'Zero Two',
        'Kaito Kuroba',
        'Rias Gremory',
        'Megumin'
    ]

    staff = [
        'Kevin Penkin',
        'LiSA',
        'Hajime Isayama',
        'Hayao Miyazaki'
    ]

    studio = [
        'Kyoto Animation',
        'Shaft',
        'White Fox',
        'A-1 Pictures'
    ]

    random = [
        'anime action',
        'anime romance',
        'anime comedy',
        'anime slice of life',
        'manga action',
        'manga romance',
        'manga comedy',
        'manga slice of life',
    ]

    themes = [
        'Shingeki no Kyojin',
        'Code Geass: Hangyaku no Lelouch',
        'Steins;Gate',
        'Fate/Zero'
    ]

    theme = [
        'OP1 Darling in the FranXX',
        'OP4 Bakemonogatari',
        'ED1 Re:Zero',
        'ED2 Kaguya-sama',
    ]

    setprofile = [
        f'al {ctx.author.name}',
        f'mal {ctx.author.name}',
        f'kitsu {ctx.author.name}'
    ]

    trending = [
        'anime',
        'manga'
    ]

    try:
        example = f'{command} {rnd.choice(locals()[command])}'
    except KeyError:
        example = None

    return example
