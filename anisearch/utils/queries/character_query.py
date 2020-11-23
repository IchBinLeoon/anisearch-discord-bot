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