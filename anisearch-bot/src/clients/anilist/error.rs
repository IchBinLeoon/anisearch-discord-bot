use graphql_client::Error as GraphQLError;
use reqwest::Error as ReqwestError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AniListError {
    #[error("{0}")]
    Request(#[from] ReqwestError),

    #[error("{0}")]
    GraphQL(GraphQLError),
}
