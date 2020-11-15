SEARCH_STUDIO_QUERY = '''
query ($search: String, $page: Int, $amount: Int) {
  Page(page: $page, perPage: $amount) {
    pageInfo {
      total
      perPage
      currentPage
      lastPage
      hasNextPage
    }
    studios(search: $search) {
        id
        name
        siteUrl
        isAnimationStudio
        favourites
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
    }
  }
}
'''
