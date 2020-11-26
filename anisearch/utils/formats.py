import datetime
import re


def clean_html(raw_text):
    cleanr = re.compile('<.*?>')
    clean_text = re.sub(cleanr, '', raw_text)
    return clean_text


def clean_spoilers(raw_text):
    cleanr = re.compile('/<span[^>]*>.*</span>/g')
    clean_text = re.sub(cleanr, '', raw_text)
    return clean_text


def description_parser(description, length):
    description = clean_spoilers(description)
    description = clean_html(description)
    description = description
    if len(description) > length:
        return description[0:length] + '...'
    else:
        return description


def anilist_date_parser(day, month, year):
    month = datetime.date(1900, month, 1).strftime('%B')
    month_day = month + ' ' + str(day)
    date = '{}, {}'.format(month_day, year)
    return date


def anilist_type_parsers(media_type):
    MediaTypeToString = {
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
    return MediaTypeToString[media_type]


def anilist_anime_status_parsers(media_status):
    AnimeStatusToString = {
        'FINISHED': 'Finished',
        'RELEASING': 'Currently Airing',
        'NOT_YET_RELEASED': 'Not Yet Aired',
        'CANCELLED': 'Cancelled'
    }
    return AnimeStatusToString[media_status]


def anilist_manga_status_parsers(media_status):
    MangaStatusToString = {
        'FINISHED': 'Finished',
        'RELEASING': 'Publishing',
        'NOT_YET_RELEASED': 'Not Yet Published',
        'CANCELLED': 'Cancelled'
    }
    return MangaStatusToString[media_status]
