use std::ops::Not;

use crate::clients::anilist::character_query::CharacterQueryPageCharacters;
use crate::clients::anilist::error::AniListError;
use crate::clients::anilist::media_query::{
    MediaQueryPageMedia, MediaSeason, MediaSort, MediaType,
};
use crate::clients::anilist::staff_query::StaffQueryPageStaff;
use crate::clients::anilist::studio_query::StudioQueryPageStudios;
use crate::clients::anilist::{
    AniListClient, character_query, media_query, staff_query, studio_query,
};
use crate::services::anilist::cache::AniListAutocompleteCache;

mod cache;
mod trie;

const DEFAULT_PAGE: i64 = 1;
const DEFAULT_SEARCH_LIMIT: usize = 10;

const AUTOCOMPLETE_LIMIT: usize = 25;
const MAX_AUTOCOMPLETE_LEN: usize = 100;

const TRENDING_LIMIT: usize = 15;
const SEASONAL_LIMIT: usize = 50;

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
        media: MediaType,
        title: Option<String>,
        limit: Option<usize>,
        sort: Option<Vec<MediaSort>>,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        let variables = media_query::Variables {
            page: Some(DEFAULT_PAGE),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            season: None,
            season_year: None,
            type_: Some(media),
            search: title,
            sort: sort.map(|v| v.into_iter().map(Some).collect()),
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
        self.search_media(
            MediaType::ANIME,
            title.is_empty().not().then_some(title),
            limit,
            None,
        )
        .await
    }

    pub async fn search_manga(
        &self,
        title: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        self.search_media(
            MediaType::MANGA,
            title.is_empty().not().then_some(title),
            limit,
            None,
        )
        .await
    }

    pub async fn search_character(
        &self,
        name: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<CharacterQueryPageCharacters>>, AniListError> {
        let variables = character_query::Variables {
            page: Some(DEFAULT_PAGE),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: name.is_empty().not().then_some(name),
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
            page: Some(DEFAULT_PAGE),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: name.is_empty().not().then_some(name),
        };

        let data = self.client.staff(variables).await?;

        let staff = Self::flatten_response_data(data, |d| d.page?.staff);

        Ok(staff)
    }

    pub async fn search_studio(
        &self,
        name: String,
        limit: Option<usize>,
    ) -> Result<Option<Vec<StudioQueryPageStudios>>, AniListError> {
        let variables = studio_query::Variables {
            page: Some(DEFAULT_PAGE),
            per_page: Some(limit.unwrap_or(DEFAULT_SEARCH_LIMIT) as i64),
            search: name.is_empty().not().then_some(name),
        };

        let data = self.client.studio(variables).await?;

        let studios = Self::flatten_response_data(data, |d| d.page?.studios);

        Ok(studios)
    }

    pub async fn trending_anime(&self) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        self.search_media(
            MediaType::ANIME,
            None,
            Some(TRENDING_LIMIT),
            Some(vec![MediaSort::TRENDING_DESC]),
        )
        .await
    }

    pub async fn trending_manga(&self) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        self.search_media(
            MediaType::MANGA,
            None,
            Some(TRENDING_LIMIT),
            Some(vec![MediaSort::TRENDING_DESC]),
        )
        .await
    }

    pub async fn seasonal(
        &self,
        season: MediaSeason,
        year: i32,
        sort: MediaSort,
    ) -> Result<Option<Vec<MediaQueryPageMedia>>, AniListError> {
        let variables = media_query::Variables {
            page: Some(DEFAULT_PAGE),
            per_page: Some(SEASONAL_LIMIT as i64),
            season: Some(season),
            season_year: Some(year as i64),
            type_: Some(MediaType::ANIME),
            search: None,
            sort: Some(vec![Some(sort)]),
        };

        let data = self.client.media(variables).await?;

        let media = Self::flatten_response_data(data, |d| d.page?.media);

        Ok(media)
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
            return Ok(Self::truncate_autocomplete_results(titles));
        }

        let anime = self.search_anime(title, Some(AUTOCOMPLETE_LIMIT)).await?;

        match anime {
            Some(anime) => {
                titles = Self::extract_media_titles(anime);

                self.autocomplete_cache
                    .insert_anime_titles(titles.clone())
                    .await;

                Ok(Self::truncate_autocomplete_results(titles))
            }
            None => Ok(vec![]),
        }
    }

    pub async fn manga_autocomplete(&self, title: String) -> Result<Vec<String>, AniListError> {
        let mut titles = self.autocomplete_cache.search_manga_titles(&title).await;

        if !titles.is_empty() {
            return Ok(Self::truncate_autocomplete_results(titles));
        }

        let manga = self.search_manga(title, Some(AUTOCOMPLETE_LIMIT)).await?;

        match manga {
            Some(manga) => {
                titles = Self::extract_media_titles(manga);

                self.autocomplete_cache
                    .insert_manga_titles(titles.clone())
                    .await;

                Ok(Self::truncate_autocomplete_results(titles))
            }
            None => Ok(vec![]),
        }
    }

    fn extract_media_titles(media: Vec<MediaQueryPageMedia>) -> Vec<String> {
        media
            .iter()
            .filter_map(|data| data.title.as_ref())
            .flat_map(|title| {
                let mut titles = vec![];

                if let Some(romaji) = &title.romaji {
                    titles.push(romaji.clone());

                    if let Some(english) = &title.english {
                        if english != romaji {
                            titles.push(english.clone());
                        }
                    }
                }

                titles
            })
            .collect()
    }

    pub async fn character_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_character_names(&name).await;

        if !names.is_empty() {
            return Ok(Self::truncate_autocomplete_results(names));
        }

        let characters = self
            .search_character(name, Some(AUTOCOMPLETE_LIMIT))
            .await?;

        match characters {
            Some(characters) => {
                names = characters
                    .iter()
                    .filter_map(|data| data.name.as_ref()?.full.clone())
                    .collect();

                self.autocomplete_cache
                    .insert_character_names(names.clone())
                    .await;

                Ok(Self::truncate_autocomplete_results(names))
            }
            None => Ok(vec![]),
        }
    }

    pub async fn staff_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_staff_names(&name).await;

        if !names.is_empty() {
            return Ok(Self::truncate_autocomplete_results(names));
        }

        let staff = self.search_staff(name, Some(AUTOCOMPLETE_LIMIT)).await?;

        match staff {
            Some(staff) => {
                names = staff
                    .iter()
                    .filter_map(|data| data.name.as_ref()?.full.clone())
                    .collect();

                self.autocomplete_cache
                    .insert_staff_names(names.clone())
                    .await;

                Ok(Self::truncate_autocomplete_results(names))
            }
            None => Ok(vec![]),
        }
    }

    pub async fn studios_autocomplete(&self, name: String) -> Result<Vec<String>, AniListError> {
        let mut names = self.autocomplete_cache.search_studio_names(&name).await;

        if !names.is_empty() {
            return Ok(Self::truncate_autocomplete_results(names));
        }

        let studios = self.search_studio(name, Some(AUTOCOMPLETE_LIMIT)).await?;

        match studios {
            Some(studios) => {
                names = studios.iter().map(|data| data.name.clone()).collect();

                self.autocomplete_cache
                    .insert_studio_names(names.clone())
                    .await;

                Ok(Self::truncate_autocomplete_results(names))
            }
            None => Ok(vec![]),
        }
    }

    fn truncate_autocomplete_results(results: Vec<String>) -> Vec<String> {
        results
            .into_iter()
            .take(AUTOCOMPLETE_LIMIT)
            .map(|s| s.chars().take(MAX_AUTOCOMPLETE_LEN).collect())
            .collect()
    }
}
