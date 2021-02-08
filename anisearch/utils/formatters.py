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

log = logging.getLogger(__name__)


def format_media_type(media_type: str) -> str:
    """
    Formats the anilist media type.
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
    Formats the anilist anime status.
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
    Formats the anilist manga status.
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
    Removes the html tags from a text.
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_text)
    return clean_text


def format_description(description: str, length: int) -> str:
    """
    Formats the anilist description.
    """
    description = clean_html(description)
    # Remove markdown
    description = description.replace('**', '').replace('__', '')
    # Replace spoiler tags
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
    Formats the anilist date.
    """
    month = datetime.date(1900, month, 1).strftime('%B')
    date = f'{month} {str(day)}, {year}'
    return date
