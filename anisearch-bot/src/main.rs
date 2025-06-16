use std::process::exit;
use std::sync::Arc;

use anisearch_lib::config::ConfigTrait;
use anisearch_lib::database::{create_database_connection, get_database_version};
use anisearch_lib::grpc::bot_server::BotServer;
use anisearch_lib::version;
use anisearch_migration::Migrator;
use anyhow::Result;
use poise::builtins::create_application_commands;
use poise::serenity_prelude::{ClientBuilder, GatewayIntents};
use poise::{Framework, FrameworkOptions};
use sea_orm::DatabaseConnection;
use tokio::spawn;
use tonic::transport::Server;
use tonic_health::server::health_reporter;
use tracing::{error, info};
use tracing_subscriber::fmt;

use crate::api::BotService;
use crate::config::Config;
use crate::error::{Error, on_error};
use crate::events::Handler;

mod api;
mod commands;
mod config;
mod error;
mod events;
mod utils;

pub type Context<'a> = poise::Context<'a, Data, Error>;

pub struct Data {
    pub database: Arc<DatabaseConnection>,
}

#[tokio::main]
async fn main() {
    fmt().init();

    if let Err(e) = init().await {
        error!("{}", e);
        exit(1);
    }
}

async fn init() -> Result<()> {
    info!("Starting AniSearch Bot v{}", version());

    let config = Config::init()?;

    let intents = GatewayIntents::default();

    let options = FrameworkOptions {
        commands: vec![commands::help::ping::ping()],
        on_error: |error| {
            Box::pin(async move {
                if let Err(e) = on_error(error).await {
                    error!("An error occurred while handling an error: {e}");
                }
            })
        },
        ..Default::default()
    };

    let handler = Handler {
        create_commands: create_application_commands(&options.commands),
        testing_guild: config.testing_guild,
    };

    let framework = Framework::new(options);

    let database = Arc::new(create_database_connection::<Migrator>(&config.database_uri).await?);

    info!(
        "Connected to database ({})",
        get_database_version(&database).await?
    );

    let data = Arc::new(Data { database });

    let mut client = ClientBuilder::new(config.token, intents)
        .data(data)
        .framework(framework)
        .event_handler(handler)
        .await?;

    let (health_reporter, health_service) = health_reporter();

    health_reporter.set_serving::<BotServer<BotService>>().await;

    let server = Server::builder()
        .add_service(health_service)
        .add_service(BotServer::new(BotService::new(
            health_reporter,
            client.http.clone(),
            client.shard_manager.runners.clone(),
        )))
        .serve(config.grpc_address.parse()?);

    spawn(async move {
        info!("Running gRPC server on {}", config.grpc_address);

        if let Err(e) = server.await {
            error!("Failed to run gRPC server: {e}");
        }
    });

    if let Some(total_shards) = config.total_shards {
        Ok(client.start_shards(total_shards).await?)
    } else {
        Ok(client.start_autosharded().await?)
    }
}
