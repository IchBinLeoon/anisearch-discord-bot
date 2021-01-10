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

SEARCH_CHARACTER_QUERY = '''
query ($search: String, $page: Int, $amount: Int) {
  Page(page: $page, perPage: $amount) {
    pageInfo {
      total
      perPage
      currentPage
      lastPage
      hasNextPage
    }
    characters(search: $search) {
        id
        name {
          first
          last
          full
          native
          alternative
        }
        image {
          large
          medium
        }
        description
        media(sort:POPULARITY_DESC) {
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
        favourites
        siteUrl
    }
  }
}
'''