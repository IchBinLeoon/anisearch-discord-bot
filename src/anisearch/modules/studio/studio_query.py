query = '''
                        query ($studio: String){
                          Studio(search: $studio) {
                            id
                            name
                            siteUrl
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
        '''