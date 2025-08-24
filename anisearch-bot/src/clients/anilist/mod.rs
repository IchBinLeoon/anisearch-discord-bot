use std::fmt;

use chrono::{DateTime, Datelike, Utc};
use graphql_client::{GraphQLQuery, Response};
use reqwest::Client;

use crate::clients::anilist::error::AniListError;

pub mod error;

const ANILIST_API_ENDPOINT: &str = "https://graphql.anilist.co";

pub struct AniListClient {
    client: Client,
}

impl AniListClient {
    pub fn new() -> Self {
        Self {
            client: Client::new(),
        }
    }

    async fn request<T: GraphQLQuery>(
        &self,
        variables: T::Variables,
    ) -> Result<Option<T::ResponseData>, AniListError> {
        let body = T::build_query(variables);

        let res = self
            .client
            .post(ANILIST_API_ENDPOINT)
            .json(&body)
            .send()
            .await?;

        let data: Response<T::ResponseData> = res.json().await?;

        if let Some(errors) = data.errors {
            return Err(AniListError::GraphQL(errors[0].clone()));
        }

        Ok(data.data)
    }

    pub async fn media(
        &self,
        variables: media_query::Variables,
    ) -> Result<Option<media_query::ResponseData>, AniListError> {
        self.request::<MediaQuery>(variables).await
    }

    pub async fn character(
        &self,
        variables: character_query::Variables,
    ) -> Result<Option<character_query::ResponseData>, AniListError> {
        self.request::<CharacterQuery>(variables).await
    }

    pub async fn staff(
        &self,
        variables: staff_query::Variables,
    ) -> Result<Option<staff_query::ResponseData>, AniListError> {
        self.request::<StaffQuery>(variables).await
    }

    pub async fn studio(
        &self,
        variables: studio_query::Variables,
    ) -> Result<Option<studio_query::ResponseData>, AniListError> {
        self.request::<StudioQuery>(variables).await
    }

    pub async fn collection(&self) -> Result<Option<collection_query::ResponseData>, AniListError> {
        self.request::<CollectionQuery>(collection_query::Variables)
            .await
    }
}

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/media.graphql",
    variables_derives = "Default",
    response_derives = "Clone, Debug",
    skip_serializing_none
)]
pub struct MediaQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/character.graphql",
    response_derives = "Clone, Debug",
    skip_serializing_none
)]
pub struct CharacterQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/staff.graphql",
    response_derives = "Clone, Debug",
    skip_serializing_none
)]
pub struct StaffQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/studio.graphql",
    response_derives = "Clone, Debug",
    skip_serializing_none
)]
pub struct StudioQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/collection.graphql",
    response_derives = "Clone, Debug"
)]
pub struct CollectionQuery;

impl media_query::MediaFormat {
    pub fn as_str(&self) -> &str {
        match self {
            media_query::MediaFormat::TV => "TV",
            media_query::MediaFormat::TV_SHORT => "TV Short",
            media_query::MediaFormat::MOVIE => "Movie",
            media_query::MediaFormat::SPECIAL => "Special",
            media_query::MediaFormat::OVA => "OVA",
            media_query::MediaFormat::ONA => "ONA",
            media_query::MediaFormat::MUSIC => "Music",
            media_query::MediaFormat::MANGA => "Manga",
            media_query::MediaFormat::NOVEL => "Novel",
            media_query::MediaFormat::ONE_SHOT => "One Shot",
            media_query::MediaFormat::Other(v) => v,
        }
    }
}

impl fmt::Display for media_query::MediaFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl media_query::MediaStatus {
    pub fn as_str(&self) -> &str {
        match self {
            media_query::MediaStatus::FINISHED => "Finished",
            media_query::MediaStatus::RELEASING => "Releasing",
            media_query::MediaStatus::NOT_YET_RELEASED => "Not Yet Released",
            media_query::MediaStatus::CANCELLED => "Cancelled",
            media_query::MediaStatus::HIATUS => "Hiatus",
            media_query::MediaStatus::Other(v) => v,
        }
    }
}

impl fmt::Display for media_query::MediaStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl media_query::MediaSource {
    pub fn as_str(&self) -> &str {
        match self {
            media_query::MediaSource::ORIGINAL => "Original",
            media_query::MediaSource::MANGA => "Manga",
            media_query::MediaSource::LIGHT_NOVEL => "Light Novel",
            media_query::MediaSource::VISUAL_NOVEL => "Visual Novel",
            media_query::MediaSource::VIDEO_GAME => "Video Game",
            media_query::MediaSource::OTHER => "Other",
            media_query::MediaSource::NOVEL => "Novel",
            media_query::MediaSource::DOUJINSHI => "Doujinshi",
            media_query::MediaSource::ANIME => "Anime",
            media_query::MediaSource::WEB_NOVEL => "Web Novel",
            media_query::MediaSource::LIVE_ACTION => "Live Action",
            media_query::MediaSource::GAME => "Game",
            media_query::MediaSource::COMIC => "Comic",
            media_query::MediaSource::MULTIMEDIA_PROJECT => "Multimedia Project",
            media_query::MediaSource::PICTURE_BOOK => "Picture Book",
            media_query::MediaSource::Other(v) => v,
        }
    }
}

impl fmt::Display for media_query::MediaSource {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl From<DateTime<Utc>> for media_query::MediaSeason {
    fn from(value: DateTime<Utc>) -> Self {
        match value.month() {
            1..=3 => media_query::MediaSeason::WINTER,
            4..=6 => media_query::MediaSeason::SPRING,
            7..=9 => media_query::MediaSeason::SUMMER,
            10..=12 => media_query::MediaSeason::FALL,
            _ => unreachable!(),
        }
    }
}

impl studio_query::MediaFormat {
    pub fn as_str(&self) -> &str {
        match self {
            studio_query::MediaFormat::TV => "TV",
            studio_query::MediaFormat::TV_SHORT => "TV Short",
            studio_query::MediaFormat::MOVIE => "Movie",
            studio_query::MediaFormat::SPECIAL => "Special",
            studio_query::MediaFormat::OVA => "OVA",
            studio_query::MediaFormat::ONA => "ONA",
            studio_query::MediaFormat::MUSIC => "Music",
            studio_query::MediaFormat::MANGA => "Manga",
            studio_query::MediaFormat::NOVEL => "Novel",
            studio_query::MediaFormat::ONE_SHOT => "One Shot",
            studio_query::MediaFormat::Other(v) => v,
        }
    }
}

impl fmt::Display for studio_query::MediaFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}
