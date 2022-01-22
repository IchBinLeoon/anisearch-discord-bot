import datetime
import logging
import re

log = logging.getLogger(__name__)


def format_media_type(media_type: str) -> str:
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
    AnimeStatus = {
        'FINISHED': 'Finished',
        'RELEASING': 'Currently Airing',
        'NOT_YET_RELEASED': 'Not Yet Aired',
        'CANCELLED': 'Cancelled'
    }
    return AnimeStatus[media_status]


def format_manga_status(media_status: str) -> str:
    MangaStatus = {
        'FINISHED': 'Finished',
        'RELEASING': 'Publishing',
        'NOT_YET_RELEASED': 'Not Yet Published',
        'CANCELLED': 'Cancelled'
    }
    return MangaStatus[media_status]


def clean_html(raw_text) -> str:
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_text)
    return clean_text


def format_description(description: str, length: int) -> str:
    description = clean_html(description)
    description = description.replace('**', '').replace('__', '')
    description = description.replace('~!', '||').replace('!~', '||')
    if len(description) > length:
        description = description[0:length]
        spoiler_tag_count = description.count('||')
        if spoiler_tag_count % 2 != 0:
            return description + '...||'
        return description + '...'
    return description


def format_date(day: int, month: int, year: int) -> str:
    month = datetime.date(1900, month, 1).strftime('%B')
    date = f'{month} {str(day)}, {year}'
    return date
