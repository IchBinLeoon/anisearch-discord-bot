use axum::Router;
use axum::routing::get;

use crate::AppState;
use crate::api::bot::commands::commands;
use crate::api::bot::shards::shards;

mod commands;
mod shards;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/commands", get(commands))
        .route("/shards", get(shards))
}
