query = '''   
                        query ($staff: String, $page: Int, $amount: Int) {
                          Page(page: $page, perPage: $amount) {
                            pageInfo {
                              total
                              perPage
                              currentPage
                              lastPage
                              hasNextPage
                            }
                            staff(search: $staff) {
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
                                language
                                description
                                favourites
                                siteUrl
                                staffMedia {
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
                                    characters {
                                      id
                                      name {
                                        first
                                        last
                                        full
                                        native
                                      }
                                    }
                                    staffRole
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
                            }
                          }
                        }
              '''
