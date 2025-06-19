use std::process::exit;
use std::sync::Arc;

use anisearch_lib::config::ConfigTrait;
use anisearch_lib::database::{create_database_connection, get_database_version};
use anisearch_lib::version;
use anisearch_migration::Migrator;
use anyhow::Result;
use axum::{Router, serve};
use sea_orm::DatabaseConnection;
use tokio::net::TcpListener;
use tonic::transport::Channel;
use tracing::{error, info};
use tracing_subscriber::fmt;

use crate::api::api;
use crate::config::Config;

mod api;
mod config;
mod error;

#[derive(Clone)]
pub struct AppState {
    pub database: Arc<DatabaseConnection>,
    pub grpc_channel: Channel,
}

#[tokio::main]
async fn main() {
    fmt().init();

    if let Err(e) = init().await {
        error!("Failed to start: {e}");
        exit(1);
    }
}

async fn init() -> Result<()> {
    info!("Starting AniSearch Web v{}", version());

    let config = Config::init()?;

    let database = Arc::new(create_database_connection::<Migrator>(&config.database_uri).await?);

    info!(
        "Connected to database ({})",
        get_database_version(&database).await?
    );

    info!("Connecting to gRPC server on {}", config.grpc_uri);

    let grpc_channel = Channel::from_shared(config.grpc_uri)?.connect().await?;

    let state = AppState {
        grpc_channel,
        database,
    };

    let app = Router::new().nest("/api", api(state));

    let listener = TcpListener::bind(config.address).await?;

    info!("Listening on {}", listener.local_addr()?);

    Ok(serve(listener, app).await?)
}
