use std::process::exit;

use anisearch_lib::config::ConfigTrait;
use anisearch_lib::version;
use anyhow::Result;
use axum::{Router, serve};
use tokio::net::TcpListener;
use tracing::{error, info};
use tracing_subscriber::fmt;

use crate::config::Config;

mod api;
mod config;

#[tokio::main]
async fn main() {
    fmt().init();

    if let Err(e) = init().await {
        error!("{}", e);
        exit(1);
    }
}

async fn init() -> Result<()> {
    info!("Starting AniSearch Web v{}", version());

    let config = Config::init()?;

    let app = Router::new().nest("/api", api::routes());

    let listener = TcpListener::bind(config.address).await?;

    info!("Listening on {}", listener.local_addr()?);

    Ok(serve(listener, app).await?)
}
