use anisearch_lib::grpc::bot_client::BotClient;
use anisearch_lib::grpc::{ShardsRequest, ShardsResponse};
use axum::Json;
use axum::extract::State;
use tonic::Request;

use crate::AppState;
use crate::error::ApiResult;

pub async fn shards(State(state): State<AppState>) -> ApiResult<Json<ShardsResponse>> {
    let mut client = BotClient::new(state.grpc_channel.clone());

    let request = Request::new(ShardsRequest {});

    let response = client.shards(request).await?;

    Ok(Json(response.into_inner()))
}
