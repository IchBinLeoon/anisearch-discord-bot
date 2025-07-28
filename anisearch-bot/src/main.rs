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
use tracing_subscriber::{EnvFilter, fmt};

use crate::api::{BotService, start_health_check};
use crate::commands::commands;
use crate::config::Config;
use crate::error::{Error, on_error};
use crate::events::{Handler, post_command, pre_command};
use crate::services::anilist::AniListService;

mod api;
mod clients;
mod commands;
mod components;
mod config;
mod error;
mod events;
mod services;
mod utils;

pub type Context<'a> = poise::Context<'a, Data, Error>;

pub struct Data {
    pub database: Arc<DatabaseConnection>,
    pub anilist_service: Arc<AniListService>,
}

#[tokio::main]
async fn main() {
    let filter = EnvFilter::try_from_default_env().unwrap_or(EnvFilter::new("info"));
    fmt().with_env_filter(filter).init();

    if let Err(e) = init().await {
        error!("Failed to start: {e}");
        exit(1);
    }
}

async fn init() -> Result<()> {
    info!("Starting AniSearch Bot v{}", version());

    let config = Config::init()?;

    let intents = GatewayIntents::default();

    let options = FrameworkOptions {
        commands: commands(),
        on_error: |error| {
            Box::pin(async move {
                if let Err(e) = on_error(error).await {
                    error!("An error occurred while handling an error: {e}");
                }
            })
        },
        pre_command: |ctx| Box::pin(pre_command(ctx)),
        post_command: |ctx| Box::pin(post_command(ctx)),
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

    let anilist_service = Arc::new(AniListService::init());

    let data = Arc::new(Data {
        database: database.clone(),
        anilist_service,
    });

    let mut client = ClientBuilder::new(config.token, intents)
        .data(data)
        .framework(framework)
        .event_handler(handler)
        .await?;

    let (health_reporter, health_service) = health_reporter();

    start_health_check(
        health_reporter,
        client.shard_manager.runners.clone(),
        database,
    );

    let bot_service = BotServer::new(BotService::new(
        client.shard_manager.runners.clone(),
        commands(),
    ));

    let server = Server::builder()
        .add_service(health_service)
        .add_service(bot_service)
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
