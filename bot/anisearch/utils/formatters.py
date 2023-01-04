import datetime
import re


def format_media_format(media_format: str) -> str:
    formats = {
        'TV': 'TV',
        'TV_SHORT': 'TV Short',
        'MOVIE': 'Movie',
        'SPECIAL': 'Special',
        'OVA': 'OVA',
        'ONA': 'ONA',
        'MUSIC': 'Music',
        'MANGA': 'Manga',
        'NOVEL': 'Novel',
        'ONE_SHOT': 'One Shot',
    }
    try:
        return formats[media_format]
    except KeyError:
        return 'N/A'


def format_anime_status(media_status: str) -> str:
    statuses = {
        'FINISHED': 'Finished',
        'RELEASING': 'Airing',
        'NOT_YET_RELEASED': 'Not Yet Aired',
        'CANCELLED': 'Cancelled',
        'HIATUS': 'Paused',
    }
    try:
        return statuses[media_status]
    except KeyError:
        return 'N/A'


def format_manga_status(media_status: str) -> str:
    statuses = {
        'FINISHED': 'Finished',
        'RELEASING': 'Publishing',
        'NOT_YET_RELEASED': 'Not Yet Published',
        'CANCELLED': 'Cancelled',
        'HIATUS': 'Paused',
    }
    try:
        return statuses[media_status]
    except KeyError:
        return 'N/A'


def format_media_source(media_source: str) -> str:
    sources = {
        'ORIGINAL': 'Original',
        'MANGA': 'Manga',
        'LIGHT_NOVEL': 'Light Novel',
        'VISUAL_NOVEL': 'Visual Novel',
        'VIDEO_GAME': 'Video Game',
        'OTHER': 'Other',
        'NOVEL': 'Novel',
        'DOUJINSHI': 'Doujinshi',
        'ANIME': 'Anime',
        'WEB_NOVEL': 'Web Novel',
        'LIVE_ACTION': 'Live Action',
        'GAME': 'Game',
        'COMIC': 'Comic',
        'MULTIMEDIA_PROJECT': 'Multimedia Project',
        'PICTURE_BOOK': 'Picture Book',
    }
    try:
        return sources[media_source]
    except KeyError:
        return 'N/A'


def format_media_title(romaji: str, english: str) -> str:
    if english is None or english == romaji:
        return romaji
    else:
        return f'{romaji} ({english})'


def clean_html(text: str) -> str:
    return re.sub('<.*?>', '', text)


def sanitize_description(description: str, length: int) -> str:
    if description is None:
        return 'N/A'

    sanitized = clean_html(description).replace('**', '').replace('__', '').replace('~!', '||').replace('!~', '||')

    if len(sanitized) > length:
        sanitized = sanitized[0:length]

        if sanitized.count('||') % 2 != 0:
            return sanitized + '...||'

        return sanitized + '...'
    return sanitized


def format_date(day: int, month: int, year: int) -> str:
    if day is None and month is None and year is None:
        return 'N/A'

    if day is None and month is None:
        return str(year)

    if day is None:
        return datetime.date(year, month, 1).strftime('%b, %Y')

    if month is None:
        return str(year)

    if year is None:
        return datetime.date(2000, month, day).strftime('%b %d')

    return datetime.date(year, month, day).strftime('%b %d, %Y')


def format_name(full: str, native: str) -> str:
    if full is None or full == native:
        return native
    elif native is None:
        return full
    else:
        return f'{full} ({native})'


def month_to_season(month: int) -> str:
    seasons = {
        1: 'WINTER',
        2: 'WINTER',
        3: 'WINTER',
        4: 'SPRING',
        5: 'SPRING',
        6: 'SPRING',
        7: 'SUMMER',
        8: 'SUMMER',
        9: 'SUMMER',
        10: 'FALL',
        11: 'FALL',
        12: 'FALL',
    }
    return seasons[month]
