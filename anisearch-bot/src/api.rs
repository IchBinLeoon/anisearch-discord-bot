use std::sync::Arc;
use std::time::Duration;

use anisearch_lib::grpc::bot_server::{Bot, BotServer};
use anisearch_lib::grpc::{
    Command, CommandOption, CommandOptionChoice, CommandsRequest, CommandsResponse, Shard,
    ShardsRequest, ShardsResponse,
};
use dashmap::DashMap;
use futures::channel::mpsc::UnboundedSender;
use poise::Command as PoiseCommand;
use poise::serenity_prelude::{ConnectionStage, ShardId, ShardRunnerInfo, ShardRunnerMessage};
use sea_orm::DatabaseConnection;
use tokio::{spawn, time};
use tonic::{Request, Response, Status, async_trait};
use tonic_health::server::HealthReporter;

use crate::Data;
use crate::error::Error;

type RunnersMap = Arc<DashMap<ShardId, (ShardRunnerInfo, UnboundedSender<ShardRunnerMessage>)>>;

pub struct BotService {
    runners: RunnersMap,
    commands: Vec<PoiseCommand<Data, Error>>,
}

impl BotService {
    pub fn new(runners: RunnersMap, commands: Vec<PoiseCommand<Data, Error>>) -> Self {
        Self { runners, commands }
    }
}

#[async_trait]
impl Bot for BotService {
    async fn commands(
        &self,
        _request: Request<CommandsRequest>,
    ) -> Result<Response<CommandsResponse>, Status> {
        let mut commands: Vec<Command> = self
            .commands
            .iter()
            .map(|c| Command {
                category: c.category.as_ref().unwrap().to_string(),
                name: c.name.to_string(),
                description: c.description.as_ref().unwrap().to_string(),
                options: c
                    .parameters
                    .iter()
                    .map(|o| CommandOption {
                        name: o.name.to_string(),
                        description: o.description.as_ref().unwrap().to_string(),
                        required: o.required,
                        choices: o
                            .choices
                            .iter()
                            .map(|c| CommandOptionChoice {
                                name: c.name.to_string(),
                            })
                            .collect(),
                    })
                    .collect(),
            })
            .collect();

        commands.sort_by(|a, b| a.category.cmp(&b.category).then(a.name.cmp(&b.name)));

        let reply = CommandsResponse { commands };

        Ok(Response::new(reply))
    }

    async fn shards(
        &self,
        _request: Request<ShardsRequest>,
    ) -> Result<Response<ShardsResponse>, Status> {
        let mut shards: Vec<Shard> = self
            .runners
            .iter()
            .map(|s| {
                let (id, (info, _)) = s.pair();

                Shard {
                    id: id.get() as u32,
                    stage: info.stage as i32,
                    latency: info.latency.map(|d| d.as_millis() as u64),
                }
            })
            .collect();

        shards.sort_by_key(|a| a.id);

        let reply = ShardsResponse { shards };

        Ok(Response::new(reply))
    }
}

pub fn start_health_check(
    health_reporter: HealthReporter,
    runners: RunnersMap,
    database: Arc<DatabaseConnection>,
) {
    spawn(async move {
        let mut interval = time::interval(Duration::from_secs(60));

        loop {
            interval.tick().await;

            let shards_healthy = runners
                .iter()
                .all(|s| s.value().0.stage != ConnectionStage::Disconnected);

            let db_healthy = database.ping().await.is_ok();

            if shards_healthy && db_healthy {
                health_reporter.set_serving::<BotServer<BotService>>().await;
            } else {
                health_reporter
                    .set_not_serving::<BotServer<BotService>>()
                    .await;
            }
        }
    });
}
