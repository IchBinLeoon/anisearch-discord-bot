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

SEARCH_MANGA_QUERY = '''
query ($search: String, $page: Int, $amount: Int) {
  Page(page: $page, perPage: $amount) {
    pageInfo {
      total
      perPage
      currentPage
      lastPage
      hasNextPage
    }
    media(search: $search, type: MANGA) {
      id
      idMal
      title {
        romaji
        english
        native
      }
      type
      format
      status
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
      season
      seasonYear
      seasonInt
      episodes
      duration
      chapters
      volumes
      countryOfOrigin
      isLicensed
      source
      hashtag
      trailer {
        id
        site
        thumbnail
      }
      coverImage {
        extraLarge
        large
        medium
        color
      }
      bannerImage
      genres
      synonyms
      averageScore
      meanScore
      popularity
      isLocked
      trending
      favourites
      tags {
        id
        name
        description
        category
        rank
        isGeneralSpoiler
        isMediaSpoiler
        isAdult
      }
      relations {
        edges {
          id
          node {
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
      }
      characters(sort:FAVOURITES_DESC) {
        edges {
          id
          node {
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
      }
      staff(sort:FAVOURITES_DESC) {
        edges {
          id
          node {
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
      }
      studios(isMain: true) {
        nodes {
        name	
        }
      }
      isAdult
      nextAiringEpisode {
        id
        airingAt
        timeUntilAiring
        episode
      }
      externalLinks {
        id
        url
        site
      }
      streamingEpisodes {
        title
        thumbnail
        url
        site
      }
      siteUrl
    }
  }
}
'''