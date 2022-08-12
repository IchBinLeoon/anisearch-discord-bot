import logging
from typing import Any, Union, Dict, List

import aiohttp

log = logging.getLogger(__name__)

API_ENDPOINT = 'https://graphql.anilist.co'


class AniListAPIError(Exception):
    def __init__(self, msg: str, status: int, locations: List[Dict[str, Any]]) -> None:
        super().__init__(f'{msg} - Status: {status} - Locations: {locations}')


class AniListClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def __aenter__(self) -> 'AniListClient':
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def _request(self, query: str, **variables: Union[str, Any]) -> Dict[str, Any]:
        r = await self.session.post(API_ENDPOINT, json={'query': query, 'variables': variables})
        log.debug(f'{r.method} {r.url} {r.status} {r.reason}')
        data = await r.json()
        if r.status != 200:
            error = data.get('errors')[0]
            raise AniListAPIError(error.get('message'), error.get('status'), error.get('locations'))
        return data

    async def media(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=self._get_media_query(), **variables)
        return data.get('data').get('Page').get('media')

    async def character(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=self._get_character_query(), **variables)
        return data.get('data').get('Page').get('characters')

    async def staff(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=self._get_staff_query(), **variables)
        return data.get('data').get('Page').get('staff')

    async def studio(self, **variables: Union[str, Any]) -> Union[List[Dict[str, Any]], None]:
        data = await self._request(query=self._get_studio_query(), **variables)
        return data.get('data').get('Page').get('studios')

    @staticmethod
    def _get_media_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $type: MediaType, $isAdult: Boolean, $genre: String, $search: String, $sort: [MediaSort]) {
          Page(page: $page, perPage: $perPage) {
            media(type: $type, isAdult: $isAdult, genre: $genre, search: $search, sort: $sort) {
              idMal
              title {
                romaji
                english
              }
              type
              format
              status(version: 2)
              description
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
              episodes
              duration
              chapters
              volumes
              source(version: 3)
              trailer {
                id
                site
              }
              coverImage {
                large
                color
              }
              bannerImage
              genres
              synonyms
              meanScore
              popularity
              favourites
              studios(isMain: true) {
                nodes {
                  name
                }
              }
              isAdult
              nextAiringEpisode {
                airingAt
                episode
              }
              externalLinks {
                url
                site
              }
              siteUrl
            }
          }
        }
        '''

    @staticmethod
    def _get_character_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            characters(search: $search) {
              name {
                full
                native
                alternative
                alternativeSpoiler
              }
              image {
                large
              }
              description
              gender
              dateOfBirth {
                year
                month
                day
              }
              age
              siteUrl
              media(sort: POPULARITY_DESC, page: 1, perPage: 5) {
                nodes {
                  title {
                    romaji
                  }
                  siteUrl
                }
              }
            }
          }
        }
        '''

    @staticmethod
    def _get_staff_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            staff(search: $search) {
              name {
                full
                native
                alternative
              }
              languageV2
              image {
                large
              }
              description
              primaryOccupations
              gender
              dateOfBirth {
                year
                month
                day
              }
              age
              homeTown
              siteUrl
              staffMedia(sort: POPULARITY_DESC, page: 1, perPage: 5) {
                nodes {
                  title {
                    romaji
                  }
                  siteUrl
                }
              }
              characters(sort: FAVOURITES_DESC, page: 1, perPage: 5) {
                nodes {
                  name {
                    full
                  }
                  siteUrl
                }
              }
            }
          }
        }
        '''

    @staticmethod
    def _get_studio_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            studios(search: $search) {
              name
              isAnimationStudio
              media(sort: POPULARITY_DESC, isMain: true, page: 1, perPage: 10) {
                nodes {
                  title {
                    romaji
                  }
                  format
                  episodes
                  coverImage {
                    large
                  }
                  siteUrl
                }
              }
              siteUrl
            }
          }
        }
        '''
