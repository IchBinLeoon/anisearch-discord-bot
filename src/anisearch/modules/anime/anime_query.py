query = '''
                query ($title: String){
                  Media(search: $title, type: ANIME) {
                    id
                    idMal
                    description
                    title {
                      romaji
                      english
                    }
                    coverImage {
                      large
                    }
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
                    synonyms
                    format
                    status
                    episodes
                    duration
                    nextAiringEpisode {
                      episode
                    }
                    averageScore
                    meanScore
                    popularity
                    favourites
                    source
                    genres
                    tags {
                      name
                    }
                    studios(isMain: true) {
                      nodes {
                        name
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
                    siteUrl
                  }
                }
        '''

query_pages = '''
                        query ($title: String, $page: Int, $amount: Int){
                          Page(page: $page, perPage: $amount) {
                            pageInfo {
                              total
                              perPage
                              currentPage
                              lastPage
                              hasNextPage
                            }
                            media(search: $title, type: ANIME) {
                              id
                              idMal
                              description
                              title {
                                romaji
                                english
                              }
                              coverImage {
                                large
                              }
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
                              synonyms
                              format
                              status
                              episodes
                              duration
                              nextAiringEpisode {
                                episode
                              }
                              averageScore
                              meanScore
                              popularity
                              favourites
                              source
                              genres
                              tags {
                                name
                              }
                              studios(isMain: true) {
                                nodes {
                                  name
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
                              siteUrl
                            }
                          }
                        }
        '''