use anisearch_lib::grpc::bot_server::Bot;
use anisearch_lib::grpc::{
    Command, CommandOption, CommandsRequest, CommandsResponse, Shard, ShardsRequest, ShardsResponse,
};
use dashmap::DashMap;
use futures::channel::mpsc::UnboundedSender;
use poise::serenity_prelude::{Http, ShardId, ShardRunnerInfo, ShardRunnerMessage};
use std::sync::Arc;
use tonic::{Request, Response, Status, async_trait};
use tonic_health::server::HealthReporter;

type RunnersMap = Arc<DashMap<ShardId, (ShardRunnerInfo, UnboundedSender<ShardRunnerMessage>)>>;

pub struct BotService {
    _health_reporter: HealthReporter,
    http: Arc<Http>,
    runners: RunnersMap,
}

impl BotService {
    pub fn new(health_reporter: HealthReporter, http: Arc<Http>, runners: RunnersMap) -> Self {
        Self {
            _health_reporter: health_reporter,
            http,
            runners,
        }
    }
}

#[async_trait]
impl Bot for BotService {
    async fn commands(
        &self,
        _request: Request<CommandsRequest>,
    ) -> Result<Response<CommandsResponse>, Status> {
        let commands = self
            .http
            .get_global_commands()
            .await
            .map_err(|e| Status::internal(e.to_string()))?;

        let reply = CommandsResponse {
            commands: commands
                .iter()
                .map(|c| Command {
                    name: c.name.to_string(),
                    description: c.description.to_string(),
                    options: c
                        .options
                        .iter()
                        .map(|o| CommandOption {
                            name: o.name.to_string(),
                            description: o.description.to_string(),
                        })
                        .collect(),
                })
                .collect(),
        };

        Ok(Response::new(reply))
    }

    async fn shards(
        &self,
        _request: Request<ShardsRequest>,
    ) -> Result<Response<ShardsResponse>, Status> {
        let reply = ShardsResponse {
            shards: self
                .runners
                .iter()
                .map(|s| {
                    let id = s.key();
                    let (info, _) = s.value();

                    Shard {
                        id: id.get() as u32,
                        stage: info.stage as i32,
                        latency: info.latency.map(|d| d.as_millis() as u64),
                    }
                })
                .collect(),
        };

        Ok(Response::new(reply))
    }
}
