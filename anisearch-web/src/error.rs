use std::error::Error;

use axum::Json;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use serde_json::json;
use thiserror::Error;
use tonic::Status;
use tracing::error;

pub type ApiResult<T, E = ApiError> = Result<T, E>;

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("internal server error")]
    Internal(#[source] Box<dyn Error>),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        if let Some(e) = self.source() {
            error!("Error: {}", e)
        }

        let status = match self {
            ApiError::Internal(_) => StatusCode::INTERNAL_SERVER_ERROR,
        };

        let value = json!({"error": self.to_string()});

        (status, Json(value)).into_response()
    }
}

impl From<Status> for ApiError {
    fn from(e: Status) -> Self {
        Self::Internal(e.into())
    }
}
