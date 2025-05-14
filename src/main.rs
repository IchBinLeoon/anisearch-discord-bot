use std::process::exit;
use std::sync::Arc;

use anyhow::Result;
use migration::Migrator;
use poise::builtins::create_application_commands;
use poise::serenity_prelude::{ClientBuilder, GatewayIntents};
use poise::{Framework, FrameworkOptions};
use sea_orm::DatabaseConnection;
use tracing::{error, info};

use crate::config::Config;
use crate::database::create_database_connection;
use crate::events::Handler;

mod commands;
mod config;
mod database;
mod events;
mod utils;

type Error = Box<dyn std::error::Error + Send + Sync>;
type Context<'a> = poise::Context<'a, Data, Error>;

pub struct Data {
    pub database: Arc<DatabaseConnection>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    if let Err(e) = init().await {
        error!("{}", e);
        exit(1);
    }
}

async fn init() -> Result<()> {
    info!("Starting AniSearch Bot");

    let config = Config::init()?;

    let intents = GatewayIntents::default();

    let options = FrameworkOptions {
        commands: vec![commands::help::ping::ping()],
        ..Default::default()
    };

    let handler = Handler {
        create_commands: create_application_commands(&options.commands),
        testing_guild: config.testing_guild,
    };

    let framework = Framework::new(options);

    let database = Arc::new(create_database_connection::<Migrator>(&config.database_uri).await?);

    let data = Arc::new(Data { database });

    let mut client = ClientBuilder::new(config.token, intents)
        .data(data)
        .framework(framework)
        .event_handler(handler)
        .await?;

    if let Some(total_shards) = config.total_shards {
        Ok(client.start_shards(total_shards).await?)
    } else {
        Ok(client.start_autosharded().await?)
    }
}
