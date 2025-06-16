use axum::Router;
use axum::routing::get;

use crate::AppState;

mod bot;

pub fn api(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health))
        .nest("/bot", bot::routes())
        .with_state(state)
}

async fn health() -> &'static str {
    "I'm healthy!"
}
