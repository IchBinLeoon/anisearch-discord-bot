import logging
import random as rnd
from typing import Union

from nextcord.ext.commands import Context

logger = logging.getLogger(__name__)


def get_command_example(ctx: Context, command: str) -> Union[str, None]:

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

    addprofile = [
        f'al {ctx.author.name}',
        f'mal {ctx.author.name}',
        f'kitsu {ctx.author.name}'
    ]

    removeprofile = [
        'al',
        'mal',
        'kitsu',
        'all'
    ]

    watch = [
        '132456',
        '107717'
    ]

    unwatch = [
        '116742',
        '235'
    ]

    trending = [
        'anime',
        'manga'
    ]

    set = [
        'channel #notifications',
        'role @Notifications'
    ]

    setprefix = [
        '?',
        '!'
    ]

    try:
        example = f'{command} {rnd.choice(locals()[command])}'
    except KeyError:
        example = None

    return example
