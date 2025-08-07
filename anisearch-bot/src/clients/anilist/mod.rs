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
}

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/media.graphql",
    skip_serializing_none
)]
pub struct MediaQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/character.graphql",
    skip_serializing_none
)]
pub struct CharacterQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/staff.graphql",
    skip_serializing_none
)]
pub struct StaffQuery;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "src/clients/anilist/queries/schema.graphql",
    query_path = "src/clients/anilist/queries/studio.graphql",
    skip_serializing_none
)]
pub struct StudioQuery;
