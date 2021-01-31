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

import datetime
import logging
import re
from typing import Dict, Any

log = logging.getLogger(__name__)


def get_media_title(data: Dict[str, Any]) -> str:
    """
    Returns the media title.
    """
    if data.get('english') is None or data.get('english') == data.get('romaji'):
        title = data.get('romaji')
    else:
        title = '{} ({})'.format(data.get('romaji'), data.get('english'))
    return title


def get_media_stats(format_: str, type_: str, status: str, mean_score: int) -> str:
    """
    Returns the media stats.
    """
    anime_stats = []
    anime_type = 'Type: ' + format_media_type(format_) if format_ else 'N/A'
    anime_stats.append(anime_type)
    anime_status = 'N/A'
    if type_ == 'ANIME':
        anime_status = 'Status: ' + format_anime_status(status)
    elif type_ == 'MANGA':
        anime_status = 'Status: ' + format_manga_status(status)
    anime_stats.append(anime_status)
    anime_score = 'Score: ' + str(mean_score) if mean_score else 'N/A'
    anime_stats.append(anime_score)
    stats = ' | '.join(anime_stats)
    return stats


def get_char_staff_name(data: Dict[str, Any]) -> str:
    """
    Returns the character/staff name.
    """
    if data.get('full') is None or data.get('full') == data.get('native'):
        name = data.get('native')
    else:
        if data.get('native') is None:
            name = data.get('full')
        else:
            name = '{} ({})'.format(data.get('full'), data.get('native'))
    return name


def format_media_type(media_type: str) -> str:
    """
    Formats the media type.
    """
    MediaType = {
        'TV': 'TV',
        'MOVIE': 'Movie',
        'OVA': 'OVA',
        'ONA': 'ONA',
        'TV_SHORT': 'TV Short',
        'MUSIC': 'Music',
        'SPECIAL': 'Special',
        'ONE_SHOT': 'One Shot',
        'NOVEL': 'Novel',
        'MANGA': 'Manga'
    }
    return MediaType[media_type]


def format_anime_status(media_status: str) -> str:
    """
    Formats the anime status.
    """
    AnimeStatus = {
        'FINISHED': 'Finished',
        'RELEASING': 'Currently Airing',
        'NOT_YET_RELEASED': 'Not Yet Aired',
        'CANCELLED': 'Cancelled'
    }
    return AnimeStatus[media_status]


def format_manga_status(media_status: str) -> str:
    """
    Formats the manga status.
    """
    MangaStatus = {
        'FINISHED': 'Finished',
        'RELEASING': 'Publishing',
        'NOT_YET_RELEASED': 'Not Yet Published',
        'CANCELLED': 'Cancelled'
    }
    return MangaStatus[media_status]


def clean_html(raw_text) -> str:
    """
    Removes the unwanted html tags.
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_text)
    return clean_text


def format_description(description: str, length: int) -> str:
    """
    Makes the anilist description suitable for an embed.
    """
    description = clean_html(description)
    description = description.replace('~!', '||').replace('!~', '||')
    if len(description) > length:
        description = description[0:length]
        spoiler_tag_count = description.count('||')
        if spoiler_tag_count % 2 != 0:
            return description + '...||'
        return description + '...'
    return description


def format_date(day: int, month: int, year: int) -> str:
    """
    Makes the anilist date suitable for an embed.
    """
    month = datetime.date(1900, month, 1).strftime('%B')
    month_day = month + ' ' + str(day)
    date = '{}, {}'.format(month_day, year)
    return date
