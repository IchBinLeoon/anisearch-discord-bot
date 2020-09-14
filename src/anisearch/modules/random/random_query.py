query_anime = '''
                        query ($genre: String, $page: Int, $amount: Int){
                          Page(page: $page, perPage: $amount) {
                            pageInfo {
                              total
                              perPage
                              currentPage
                              lastPage
                              hasNextPage
                            }
                            media(genre: $genre, type: ANIME, sort:POPULARITY_DESC) {
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

query_manga = '''
                        query ($genre: String, $page: Int, $amount: Int){
                          Page(page: $page, perPage: $amount) {
                            pageInfo {
                              total
                              perPage
                              currentPage
                              lastPage
                              hasNextPage
                            }
                            media(genre: $genre, type: MANGA, sort:POPULARITY_DESC) {
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
                                synonyms
                                format
                                status
                                chapters
                                volumes
                                averageScore
                                meanScore
                                popularity
                                favourites
                                source
                                genres
                                tags {
                                  name
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