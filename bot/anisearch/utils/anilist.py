import logging
from typing import Any, Dict, List

import aiohttp

log = logging.getLogger(__name__)

API_ENDPOINT = 'https://graphql.anilist.co'


class AniListException(Exception):
    def __init__(self, status: int, message: str, locations: List[Dict[str, Any]]) -> None:
        self.status = status
        self.message = message
        self.locations = locations

        msg = f'status={self.status}, message="{self.message}"'
        if self.locations:
            msg += f', locations={self.locations}'

        super().__init__(msg)


class AniListClient:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'AniListClient':
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def _request(self, query: str, **variables: Dict[str, Any]) -> Dict[str, Any]:
        r = await self.session.post(API_ENDPOINT, json={'query': query, 'variables': variables})
        log.debug(f'{r.method} {r.url} {r.status} {r.reason}')
        data = await r.json()
        if r.status != 200:
            error = data.get('errors')[0]
            raise AniListException(error.get('status'), error.get('message'), error.get('locations'))
        return data

    async def media(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_media_query(), **variables)
        return data.get('data').get('Page').get('media')

    async def character(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_character_query(), **variables)
        return data.get('data').get('Page').get('characters')

    async def staff(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_staff_query(), **variables)
        return data.get('data').get('Page').get('staff')

    async def studio(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_studio_query(), **variables)
        return data.get('data').get('Page').get('studios')

    async def user(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_user_query(), **variables)
        return data.get('data').get('Page').get('users')

    async def schedule(self, **variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = await self._request(query=self._get_schedule_query(), **variables)
        return data.get('data').get('Page').get('airingSchedules')

    @staticmethod
    def _get_media_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $id: Int, $season: MediaSeason, $seasonYear: Int, $type: MediaType, $isAdult: Boolean, $countryOfOrigin: CountryCode, $search: String, $genres: [String], $tags: [String], $sort: [MediaSort]) {
          Page(page: $page, perPage: $perPage) {
            media(id: $id, season: $season, seasonYear: $seasonYear, type: $type, isAdult: $isAdult, countryOfOrigin: $countryOfOrigin, search: $search, genre_in: $genres, tag_in: $tags, sort: $sort) {
              id
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
                  isAdult
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
                  isAdult
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
                  isAdult
                  siteUrl
                }
              }
              siteUrl
            }
          }
        }
        '''

    @staticmethod
    def _get_user_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $id: Int, $name: String) {
          Page(page: $page, perPage: $perPage) {
            users(id: $id, name: $name) {
              id
              name
              about
              avatar {
                large
              }
              bannerImage
              favourites {
                anime {
                  nodes {
                    title {
                      romaji
                    }
                    siteUrl
                  }
                }
                manga {
                  nodes {
                    title {
                      romaji
                    }
                    siteUrl
                  }
                }
                characters {
                  nodes {
                    name {
                      full
                    }
                    siteUrl
                  }
                }
                staff {
                  nodes {
                    name {
                      full
                    }
                    siteUrl
                  }
                }
                studios {
                  nodes {
                    name
                    siteUrl
                  }
                }
              }
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
              siteUrl
            }
          }
        }
        '''

    @staticmethod
    def _get_schedule_query() -> str:
        return '''
        query ($page: Int, $perPage: Int, $notYetAired: Boolean, $sort: [AiringSort]) {
          Page(page: $page, perPage: $perPage) {
            airingSchedules(notYetAired: $notYetAired, sort: $sort) {
              id
              timeUntilAiring
              episode
              media {
                id
                idMal
                title {
                  romaji
                  english
                }
                episodes
                coverImage {
                  large
                }
                siteUrl
                isAdult
                countryOfOrigin
              }
            }
          }
        }
        '''


GENRES = [
    'Action',
    'Adventure',
    'Comedy',
    'Drama',
    'Ecchi',
    'Fantasy',
    'Horror',
    'Mahou Shoujo',
    'Mecha',
    'Music',
    'Mystery',
    'Psychological',
    'Romance',
    'Sci-Fi',
    'Slice of Life',
    'Sports',
    'Supernatural',
    'Thriller',
]

TAGS = [
    '4-koma',
    'Achromatic',
    'Achronological Order',
    'Acting',
    'Adoption',
    'Advertisement',
    'Afterlife',
    'Age Gap',
    'Age Regression',
    'Agender',
    'Agriculture',
    'Airsoft',
    'Aliens',
    'Alternate Universe',
    'American Football',
    'Amnesia',
    'Anachronism',
    'Angels',
    'Animals',
    'Anthology',
    'Anti-Hero',
    'Archery',
    'Artificial Intelligence',
    'Asexual',
    'Assassins',
    'Astronomy',
    'Athletics',
    'Augmented Reality',
    'Autobiographical',
    'Aviation',
    'Badminton',
    'Band',
    'Bar',
    'Baseball',
    'Basketball',
    'Battle Royale',
    'Biographical',
    'Bisexual',
    'Body Horror',
    'Body Swapping',
    'Boxing',
    "Boys' Love",
    'Bullying',
    'Butler',
    'Calligraphy',
    'Cannibalism',
    'Card Battle',
    'Cars',
    'Centaur',
    'CGI',
    'Cheerleading',
    'Chibi',
    'Chimera',
    'Chuunibyou',
    'Circus',
    'Classic Literature',
    'Clone',
    'College',
    'Coming of Age',
    'Conspiracy',
    'Cosmic Horror',
    'Cosplay',
    'Crime',
    'Crossdressing',
    'Crossover',
    'Cult',
    'Cultivation',
    'Cute Boys Doing Cute Things',
    'Cute Girls Doing Cute Things',
    'Cyberpunk',
    'Cyborg',
    'Cycling',
    'Dancing',
    'Death Game',
    'Delinquents',
    'Demons',
    'Denpa',
    'Detective',
    'Dinosaurs',
    'Disability',
    'Dissociative Identities',
    'Dragons',
    'Drawing',
    'Drugs',
    'Dullahan',
    'Dungeon',
    'Dystopian',
    'E-Sports',
    'Economics',
    'Educational',
    'Elf',
    'Ensemble Cast',
    'Environmental',
    'Episodic',
    'Ero Guro',
    'Espionage',
    'Fairy Tale',
    'Family Life',
    'Fashion',
    'Female Harem',
    'Female Protagonist',
    'Fencing',
    'Firefighters',
    'Fishing',
    'Fitness',
    'Flash',
    'Food',
    'Football',
    'Foreign',
    'Fugitive',
    'Full CGI',
    'Full Color',
    'Gambling',
    'Gangs',
    'Gender Bending',
    'Ghost',
    'Go',
    'Goblin',
    'Gods',
    'Golf',
    'Gore',
    'Guns',
    'Gyaru',
    'Henshin',
    'Heterosexual',
    'Hikikomori',
    'Historical',
    'Ice Skating',
    'Idol',
    'Isekai',
    'Iyashikei',
    'Josei',
    'Judo',
    'Kaiju',
    'Karuta',
    'Kemonomimi',
    'Kids',
    'Kuudere',
    'Lacrosse',
    'Language Barrier',
    'LGBTQ+ Themes',
    'Lost Civilization',
    'Love Triangle',
    'Mafia',
    'Magic',
    'Mahjong',
    'Maids',
    'Makeup',
    'Male Harem',
    'Male Protagonist',
    'Martial Arts',
    'Medicine',
    'Memory Manipulation',
    'Mermaid',
    'Meta',
    'Military',
    'Monster Boy',
    'Monster Girl',
    'Mopeds',
    'Motorcycles',
    'Musical',
    'Mythology',
    'Necromancy',
    'Nekomimi',
    'Ninja',
    'No Dialogue',
    'Noir',
    'Non-fiction',
    'Nudity',
    'Nun',
    'Office Lady',
    'Oiran',
    'Ojou-sama',
    'Otaku Culture',
    'Outdoor',
    'Pandemic',
    'Parkour',
    'Parody',
    'Philosophy',
    'Photography',
    'Pirates',
    'Poker',
    'Police',
    'Politics',
    'Post-Apocalyptic',
    'POV',
    'Primarily Adult Cast',
    'Primarily Child Cast',
    'Primarily Female Cast',
    'Primarily Male Cast',
    'Primarily Teen Cast',
    'Puppetry',
    'Rakugo',
    'Real Robot',
    'Rehabilitation',
    'Reincarnation',
    'Religion',
    'Revenge',
    'Robots',
    'Rotoscoping',
    'Rugby',
    'Rural',
    'Samurai',
    'Satire',
    'School',
    'School Club',
    'Scuba Diving',
    'Seinen',
    'Shapeshifting',
    'Ships',
    'Shogi',
    'Shoujo',
    'Shounen',
    'Shrine Maiden',
    'Skateboarding',
    'Skeleton',
    'Slapstick',
    'Slavery',
    'Software Development',
    'Space',
    'Space Opera',
    'Steampunk',
    'Stop Motion',
    'Succubus',
    'Suicide',
    'Sumo',
    'Super Power',
    'Super Robot',
    'Superhero',
    'Surfing',
    'Surreal Comedy',
    'Survival',
    'Swimming',
    'Swordplay',
    'Table Tennis',
    'Tanks',
    'Tanned Skin',
    'Teacher',
    "Teens' Love",
    'Tennis',
    'Terrorism',
    'Time Manipulation',
    'Time Skip',
    'Tokusatsu',
    'Tomboy',
    'Torture',
    'Tragedy',
    'Trains',
    'Transgender',
    'Travel',
    'Triads',
    'Tsundere',
    'Twins',
    'Urban',
    'Urban Fantasy',
    'Vampire',
    'Video Games',
    'Vikings',
    'Villainess',
    'Virtual World',
    'Volleyball',
    'VTuber',
    'War',
    'Werewolf',
    'Witch',
    'Work',
    'Wrestling',
    'Writing',
    'Wuxia',
    'Yakuza',
    'Yandere',
    'Youkai',
    'Yuri',
    'Zombie',
]
