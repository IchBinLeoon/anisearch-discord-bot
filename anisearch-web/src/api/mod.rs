use axum::Router;
use axum::routing::get;

pub fn routes() -> Router {
    Router::new().route("/health", get(health))
}

async fn health() -> &'static str {
    "I'm healthy!"
}
