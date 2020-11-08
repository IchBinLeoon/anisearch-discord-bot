query = '''
               query ($username: String){
                  User(search: $username) {
                    id
                    name
                    avatar {
                      large
                      medium
                    }
                    about
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
                      manga {
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
                      characters {
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
                      staff {
                        edges {
                          id
                          node{
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
                      studios {
                        edges {
                          id
                          node {
                            id
                            siteUrl
                            name
                          }
                        }
                      }
                    }
                    siteUrl
                  }
                }
        '''