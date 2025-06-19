use axum::Router;
use axum::extract::State;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::get;
use tonic::Request;
use tonic_health::pb::HealthCheckRequest;
use tonic_health::pb::health_client::HealthClient;

use crate::AppState;

mod bot;

pub fn api(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health))
        .nest("/bot", bot::routes())
        .with_state(state)
}

async fn health(State(state): State<AppState>) -> impl IntoResponse {
    let db_healthy = state.database.ping().await.is_ok();

    let mut client = HealthClient::new(state.grpc_channel.clone());

    let request = Request::new(HealthCheckRequest {
        service: "bot.Bot".to_string(),
    });

    let grpc_healthy = client.check(request).await.is_ok();

    if db_healthy && grpc_healthy {
        (StatusCode::OK, "I'm healthy!")
    } else {
        (StatusCode::INTERNAL_SERVER_ERROR, "I'm not healthy!")
    }
}
