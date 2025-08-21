use axum::Router;
use axum::routing::get;

use crate::AppState;
use crate::api::bot::commands::commands;
use crate::api::bot::shards::shards;
use crate::api::bot::stats::stats;

mod commands;
mod shards;
mod stats;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/stats", get(stats))
        .route("/commands", get(commands))
        .route("/shards", get(shards))
}
