use crate::clients::anilist::character_query::CharacterQueryPageCharacters;
use crate::clients::anilist::error::AniListError;
use crate::clients::anilist::media_query::{MediaQueryPageMedia, MediaType};
use crate::clients::anilist::staff_query::StaffQueryPageStaff;
use crate::clients::anilist::studio_query::StudioQueryPageStudios;
use crate::clients::anilist::{
    AniListClient, character_query, media_query, staff_query, studio_query,
};
use crate::services::anilist::cache::AniListAutocompleteCache;

mod cache;
mod trie;

const DEFAULT_SEARCH_LIMIT: usize = 10;
const AUTOCOMPLETE_LIMIT: usize = 25;

pub struct AniListService {
    client: AniListClient,
    autocomplete_cache: AniListAutocompleteCache,
}

impl AniListService {
    pub fn init() -> Self {
        Self {
            client: AniListClient::new(),
            autocomplete_cache: AniListAutocompleteCache::new(),
        }
    }

    async fn search_media(
        &self,
        title: String,
        type_: MediaType,
        limit: Option<usize>,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        let variables = media_query::Variables {
            page: Some(1),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            type_: Some(type_),
            search: Some(title),
        };

        let data = self.client.media(variables).await?;

        let media = Self::flatten_response_data(data, |d| d.page?.media);

        Ok(media)
    }

    pub async fn search_anime(
        &self,
        title: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        self.search_media(title, MediaType::ANIME, limit).await
    }

    pub async fn search_manga(
        &self,
        title: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        self.search_media(title, MediaType::MANGA, limit).await
    }

    pub async fn search_character(
        &self,
        name: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<CharacterQueryPageCharacters>>, AniListError> {
        let variables = character_query::Variables {
            page: Some(1),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: Some(name),
        };

        let data = self.client.character(variables).await?;

        let characters = Self::flatten_response_data(data, |d| d.page?.characters);

        Ok(characters)
    }

    pub async fn search_staff(
        &self,
        name: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<StaffQueryPageStaff>>, AniListError> {
        let variables = staff_query::Variables {
            page: Some(1),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: Some(name),
        };

        let data = self.client.staff(variables).await?;

        let staff = Self::flatten_response_data(data, |d| d.page?.staff);

        Ok(staff)
    }

    pub async fn search_sudios(
        &self,
        name: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<StudioQueryPageStudios>>, AniListError> {
        let variables = studio_query::Variables {
            page: Some(1),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: Some(name),
        };

        let data = self.client.studio(variables).await?;

        let studios = Self::flatten_response_data(data, |d| d.page?.studios);

        Ok(studios)
    }

    fn flatten_response_data<T, U, F>(data: Option<T>, extract: F) -> Option<Vec<U>>
    where
        F: FnOnce(T) -> Option<Vec<Option<U>>>,
    {
        let inner = extract(data?)?;
        let vec: Vec<U> = inner.into_iter().flatten().collect();

        if vec.is_empty() { None } else { Some(vec) }
    }

    pub async fn anime_autocomplete(&self, title: String) -> Result<Vec<String>, AniListError> {
        let mut titles = self.autocomplete_cache.search_anime_titles(&title).await;

        if !titles.is_empty() {
            return Ok(titles);
        }

        let anime = self.search_anime(title, Some(AUTOCOMPLETE_LIMIT)).await?;

        match anime {
            Some(anime) => {
                titles = anime
                    .iter()
                    .filter_map(|data| data.title.as_ref()?.romaji.to_owned())
                    .collect();

                self.autocomplete_cache
                    .insert_anime_titles(titles.clone())
                    .await;

                Ok(titles)
            }
            None => Ok(vec![]),
        }
    }

    pub async fn manga_autocomplete(&self, title: String) -> Result<Vec<String>, AniListError> {
        let mut titles = self.autocomplete_cache.search_manga_titles(&title).await;

        if !titles.is_empty() {
            return Ok(titles);
        }

        let manga = self.search_manga(title, Some(AUTOCOMPLETE_LIMIT)).await?;

        match manga {
            Some(manga) => {
                titles = manga
                    .iter()
                    .filter_map(|data| data.title.as_ref()?.romaji.to_owned())
                    .collect();

                self.autocomplete_cache
                    .insert_manga_titles(titles.clone())
                    .await;

                Ok(titles)
            }
            None => Ok(vec![]),
        }
    }

    pub async fn character_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_character_names(&name).await;

        if !names.is_empty() {
            return Ok(names);
        }

        let characters = self
            .search_character(name, Some(AUTOCOMPLETE_LIMIT))
            .await?;

        match characters {
            Some(characters) => {
                names = characters
                    .iter()
                    .filter_map(|data| data.name.as_ref()?.full.to_owned())
                    .collect();

                self.autocomplete_cache
                    .insert_character_names(names.clone())
                    .await;

                Ok(names)
            }
            None => Ok(vec![]),
        }
    }

    pub async fn staff_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_staff_names(&name).await;

        if !names.is_empty() {
            return Ok(names);
        }

        let staff = self.search_staff(name, Some(AUTOCOMPLETE_LIMIT)).await?;

        match staff {
            Some(staff) => {
                names = staff
                    .iter()
                    .filter_map(|data| data.name.as_ref()?.full.to_owned())
                    .collect();

                self.autocomplete_cache
                    .insert_staff_names(names.clone())
                    .await;

                Ok(names)
            }
            None => Ok(vec![]),
        }
    }

    pub async fn studios_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_studio_names(&name).await;

        if !names.is_empty() {
            return Ok(names);
        }

        let studios = self.search_sudios(name, Some(AUTOCOMPLETE_LIMIT)).await?;

        match studios {
            Some(studios) => {
                names = studios.iter().map(|data| data.name.to_owned()).collect();

                self.autocomplete_cache
                    .insert_studio_names(names.clone())
                    .await;

                Ok(names)
            }
            None => Ok(vec![]),
        }
    }
}
