use anisearch_lib::grpc::bot_client::BotClient;
use anisearch_lib::grpc::{CommandsRequest, CommandsResponse};
use axum::Json;
use axum::extract::State;
use tonic::Request;

use crate::AppState;
use crate::error::ApiResult;

pub async fn commands(State(state): State<AppState>) -> ApiResult<Json<CommandsResponse>> {
    let mut client = BotClient::new(state.grpc_channel.clone());

    let request = Request::new(CommandsRequest {});

    let response = client.commands(request).await?;

    Ok(Json(response.into_inner()))
}
