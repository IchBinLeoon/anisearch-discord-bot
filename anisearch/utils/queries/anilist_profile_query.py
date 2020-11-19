SEARCH_ANILIST_PROFILE_QUERY = '''
query ($search: String){
  User(search: $search) {
    id
    name
    avatar {
      large
      medium
    }
    about
    bannerImage
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
    mediaListOptions {
      scoreFormat
      rowOrder
      useLegacyLists
      sharedTheme
      sharedThemeEnabled
      animeList {
        splitCompletedSectionByFormat
        theme
        advancedScoringEnabled
      }
      mangaList {
        splitCompletedSectionByFormat
        theme
        advancedScoringEnabled
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