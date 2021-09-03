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
from typing import Any, Optional, Union, Dict, List

import aiohttp

from anisearch.utils.constants import ANILIST_API_ENDPOINT

log = logging.getLogger(__name__)


class AnilistException(Exception):
    pass


class AnilistAPIError(AnilistException):

    def __init__(self, msg: str, status: int, locations: List[Dict[str, Any]]) -> None:
        super().__init__(
            f'{msg} - Status: {str(status)} - Locations: {locations}')


class AniListClient:

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()

    async def _session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, query: str, **variables: Union[str, Any]) -> Dict[str, Any]:
        session = await self._session()
        response = await session.post(ANILIST_API_ENDPOINT, json={'query': query, 'variables': variables})
        data = await response.json()
        if data.get('errors'):
            raise AnilistAPIError(data.get('errors')[0]['message'], data.get('errors')[0]['status'],
                                  data.get('errors')[0].get('locations'))
        return data

    async def media(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=Query.media(), **variables)
        if data.get('data')['Page']['media']:
            return data.get('data')['Page']['media']
        return None

    async def character(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=Query.character(), **variables)
        if data.get('data')['Page']['characters']:
            return data.get('data')['Page']['characters']
        return None

    async def staff(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=Query.staff(), **variables)
        if data.get('data')['Page']['staff']:
            return data.get('data')['Page']['staff']
        return None

    async def studio(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=Query.studio(), **variables)
        if data.get('data')['Page']['studios']:
            return data.get('data')['Page']['studios']
        return None

    async def genre(self, **variables: Union[str, Any]) -> Union[Dict[str, Any], None]:
        data = await self._request(query=Query.genre(), **variables)
        if data:
            return data
        return None

    async def tag(self, **variables: Union[str, Any]) -> Union[Dict[str, Any], None]:
        data = await self._request(query=Query.tag(), **variables)
        if data:
            return data
        return None

    async def user(self, **variables: Union[str, Any]) -> Union[Dict[str, Any], None]:
        data = await self._request(query=Query.user(), **variables)
        if data.get('data')['Page']['users']:
            return data.get('data')['Page']['users'][0]
        return None

    async def schedule(self, **variables: Union[str, Any]) -> Union[Dict[str, Any], None]:
        data = await self._request(query=Query.schedule(), **variables)
        if data.get('data')['Page']['airingSchedules']:
            return data.get('data')['Page']['airingSchedules']
        return None

    async def trending(self, **variables: Union[str, Any]) -> Union[Dict[str, Any], None]:
        data = await self._request(query=Query.trending(), **variables)
        if data.get('data')['Page']['media']:
            return data.get('data')['Page']['media']
        return None


class Query:

    @classmethod
    def media(cls) -> str:
        MEDIA_QUERY: str = '''
        query ($page: Int, $perPage: Int, $search: String, $type: MediaType) {
          Page(page: $page, perPage: $perPage) {
            media(search: $search, type: $type) {
              idMal
              title {
                romaji
                english
              }
              coverImage {
                large
                color
              }
              description
              bannerImage
              format
              status
              type
              meanScore
              startDate {
                year
                month
                day
              }
              endDate {
                year
                month
                day
              }
              duration
              source
              episodes
              chapters
              volumes
              studios {
                nodes {
                  name
                }
              }
              synonyms
              genres
              trailer {
                id
                site
              }
              externalLinks {
                site
                url
              }
              siteUrl
              isAdult
              nextAiringEpisode {
                episode
                timeUntilAiring
              }
            }
          }
        }
        '''
        return MEDIA_QUERY

    @classmethod
    def character(cls) -> str:
        CHARACTER_QUERY: str = '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            characters(search: $search) {
              name {
                full
                native
                alternative
              }
              image {
                large
              }
              description
              siteUrl
              media(perPage: 6) {
                nodes {
                  siteUrl
                  title {
                    romaji
                  }
                }
              }
            }
          }
        }
        '''
        return CHARACTER_QUERY

    @classmethod
    def staff(cls) -> str:
        STAFF_QUERY: str = '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            staff(search: $search) {
              name {
                full
                native
              }
              language
              image {
                large
              }
              description
              siteUrl
              staffMedia(perPage: 6) {
                nodes {
                  siteUrl
                  title {
                    romaji
                  }
                }
              }
              characters(perPage: 6) {
                nodes {
                  id
                  siteUrl
                  name {
                    full
                  }
                }
              }
            }
          }
        }
        '''
        return STAFF_QUERY

    @classmethod
    def studio(cls) -> str:
        STUDIO_QUERY: str = '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            studios(search: $search) {
              name
              media(sort: POPULARITY_DESC, perPage: 10, isMain: true) {
                nodes {
                  siteUrl
                  title {
                    romaji
                  }
                  format
                  episodes
                  coverImage {
                    large
                  }
                }
              }
              isAnimationStudio
              siteUrl
            }
          }
        }
        '''
        return STUDIO_QUERY

    @classmethod
    def genre(cls) -> str:
        GENRE_QUERY: str = '''
        query ($page: Int, $perPage: Int, $genre: String, $type: MediaType, $format_in: [MediaFormat]) {
          Page(page: $page, perPage: $perPage) {
            pageInfo {
              lastPage
            }
            media(genre: $genre, type: $type, format_in: $format_in) {
              idMal
              title {
                romaji
                english
              }
              coverImage {
                large
                color
              }
              description
              bannerImage
              format
              status
              type
              meanScore
              startDate {
                year
                month
                day
              }
              endDate {
                year
                month
                day
              }
              duration
              source
              episodes
              chapters
              volumes
              studios {
                nodes {
                  name
                }
              }
              synonyms
              genres
              trailer {
                id
                site
              }
              externalLinks {
                site
                url
              }
              siteUrl
              isAdult
              nextAiringEpisode {
                episode
                timeUntilAiring
              }
            }
          }
        }
        '''
        return GENRE_QUERY

    @classmethod
    def tag(cls) -> str:
        TAG_QUERY: str = '''
        query ($page: Int, $perPage: Int, $tag: String, $type: MediaType, $format_in: [MediaFormat]) {
          Page(page: $page, perPage: $perPage) {
            pageInfo {
              lastPage
            }
            media(tag: $tag, type: $type, format_in: $format_in) {
              idMal
              title {
                romaji
                english
              }
              coverImage {
                large
                color
              }
              description
              bannerImage
              format
              status
              type
              meanScore
              startDate {
                year
                month
                day
              }
              endDate {
                year
                month
                day
              }
              duration
              source
              episodes
              chapters
              volumes
              studios {
                nodes {
                  name
                }
              }
              synonyms
              genres
              trailer {
                id
                site
              }
              externalLinks {
                site
                url
              }
              siteUrl
              isAdult
              nextAiringEpisode {
                episode
                timeUntilAiring
              }
            }
          }
        }
        '''
        return TAG_QUERY

    @classmethod
    def user(cls) -> str:
        USER_QUERY: str = '''
        query ($page: Int, $perPage: Int, $name: String) {
          Page(page: $page, perPage: $perPage) {
            users(name: $name) {
              name
              avatar {
                large
                medium
              }
              about
              bannerImage
              statistics {
                anime {
                  count
                  meanScore
                  minutesWatched
                  episodesWatched
                }
                manga {
                  count
                  meanScore
                  chaptersRead
                  volumesRead
                }
              }
              favourites {
                anime {
                  nodes {
                    id
                    siteUrl
                    title {
                      romaji
                      english
                      native
                      userPreferred
                    }
                  }
                }
                manga {
                  nodes {
                    id
                    siteUrl
                    title {
                      romaji
                      english
                      native
                      userPreferred
                    }
                  }
                }
                characters {
                  nodes {
                    id
                    siteUrl
                    name {
                      first
                      last
                      full
                      native
                    }
                  }
                }
                staff {
                  nodes {
                    id
                    siteUrl
                    name {
                      first
                      last
                      full
                      native
                    }
                  }
                }
                studios {
                  nodes {
                    id
                    siteUrl
                    name
                  }
                }
              }
              siteUrl
            }
          }
        }
        '''
        return USER_QUERY

    @classmethod
    def schedule(cls) -> str:
        SCHEDULE_QUERY: str = '''
        query ($page: Int, $perPage: Int, $notYetAired: Boolean, $sort: [AiringSort]) {
          Page(page: $page, perPage: $perPage) {
            airingSchedules(notYetAired: $notYetAired, sort: $sort) {
              timeUntilAiring
              airingAt
              episode
              media {
                id
                idMal
                siteUrl
                title {
                  romaji
                  english
                }
                coverImage {
                  large
                }
                externalLinks {
                  site
                  url
                }
                duration
                format
                isAdult
                trailer {
                  id
                  site
                }
              }
            }
          }
        }
        '''
        return SCHEDULE_QUERY

    @classmethod
    def trending(cls) -> str:
        TRENDING_QUERY: str = '''
        query ($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort]) {
          Page(page: $page, perPage: $perPage) {
            media(type: $type, sort: $sort) {
              idMal
              title {
                romaji
                english
              }
              coverImage {
                large
                color
              }
              description
              bannerImage
              format
              status
              type
              meanScore
              startDate {
                year
                month
                day
              }
              endDate {
                year
                month
                day
              }
              duration
              source
              episodes
              chapters
              volumes
              studios {
                nodes {
                  name
                }
              }
              synonyms
              genres
              trailer {
                id
                site
              }
              externalLinks {
                site
                url
              }
              siteUrl
              isAdult
              nextAiringEpisode {
                episode
                timeUntilAiring
              }
            }
          }
        }
        '''
        return TRENDING_QUERY
