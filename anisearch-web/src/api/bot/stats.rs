use anisearch_lib::grpc::bot_client::BotClient;
use anisearch_lib::grpc::{StatsRequest, StatsResponse};
use axum::Json;
use axum::extract::State;
use tonic::Request;

use crate::AppState;
use crate::error::ApiResult;

pub async fn stats(State(state): State<AppState>) -> ApiResult<Json<StatsResponse>> {
    let mut client = BotClient::new(state.grpc_channel.clone());

    let request = Request::new(StatsRequest {});

    let response = client.stats(request).await?;

    Ok(Json(response.into_inner()))
}
