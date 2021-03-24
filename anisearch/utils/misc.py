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
import random

from discord.ext.commands import Context

logger = logging.getLogger(__name__)


def get_command_example(ctx: Context, command: str) -> str:
    """
    Returns an example of the specified command.

    Args:
        ctx (Context): The context in which the command was invoked under.
        command (str): The specified command.

    Returns:
        str: The command example.
    """
    if command == 'anime':
        example = f"{command} {random.choice(['Sword Art Online', 'Shingeki no Kyojin', 'Death Note', 'Steins;Gate'])}"

    elif command == 'manga':
        example = f"{command} {random.choice(['Shingeki no Kyojin', 'One Piece', 'Tokyo Ghoul', 'Jujutsu Kaisen'])}"

    elif command == 'character':
        example = f"{command} {random.choice(['Zero Two', 'Kaito Kuroba', 'Rias Gremory', 'Megumin'])}"

    elif command == 'staff':
        example = f"{command} {random.choice(['Kevin Penkin', 'LiSA', 'Hajime Isayama', 'Hayao Miyazaki'])}"

    elif command == 'studio':
        example = f"{command} {random.choice(['Kyoto Animation', 'Shaft', 'White Fox', 'A-1 Pictures'])}"

    elif command == 'random':
        example = f"{command} {random.choice(['anime', 'manga'])} {random.choice(['action', 'romance', 'comedy'])}"

    elif command == 'themes':
        example = f"{command} {random.choice(['Sword Art Online', 'Shingeki no Kyojin', 'Death Note', 'Steins;Gate'])}"

    elif command == 'theme':
        example = f"{command} {random.choice(['OP', 'OP1', 'OP2', 'OP3', 'ED', 'ED1'])} Bakemonogatari"

    elif command in ['anilist', 'myanimelist', 'kitsu']:
        example = random.choice([command, f"{command} {random.choice([ctx.author.name, f'@{ctx.author}'])}"])

    elif command == 'setprofile':
        example = f"{command} {random.choice(['al', 'mal', 'kitsu'])} {ctx.author.name}"

    elif command == 'profiles':
        example = random.choice([command, f"{command} @{ctx.author}"])

    else:
        example = None

    return example
