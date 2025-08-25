use std::collections::HashMap;
use std::sync::{Arc, LazyLock};
use std::time::Duration;

use anisearch_lib::version;
use humantime::format_duration;
use poise::async_trait;
use poise::serenity_prelude::{
    ActivityData, CacheHttp, Command, Context as SerenityContext, CreateCommand,
    Error as SerenityError, EventHandler, FullEvent, GuildId, Http, Ready, ShardId,
};
use tokio::sync::RwLock;
use tokio::time::Instant;
use tracing::{error, info, warn};

use crate::Context;
use crate::services::guild::GuildService;
use crate::utils::commands::{CommandType, ExecutionStatus};

pub static SHARD_START_TIMES: LazyLock<RwLock<HashMap<ShardId, Instant>>> =
    LazyLock::new(|| RwLock::new(HashMap::new()));

pub struct Handler {
    pub create_commands: Vec<CreateCommand<'static>>,
    pub testing_guild: Option<GuildId>,
    pub guild_service: Arc<GuildService>,
}

#[async_trait]
impl EventHandler for Handler {
    async fn dispatch(&self, ctx: &SerenityContext, event: &FullEvent) {
        match event {
            FullEvent::Ready { data_about_bot, .. } => {
                self.handle_ready(ctx, data_about_bot).await;
            }
            FullEvent::GuildCreate { guild, is_new, .. } => {
                if matches!(is_new, Some(true)) {
                    self.handle_guild_join(guild.id).await
                }
            }
            FullEvent::GuildDelete { incomplete, .. } => {
                self.handle_guild_leave(incomplete.id).await
            }
            _ => {}
        }
    }
}

impl Handler {
    async fn handle_ready(&self, ctx: &SerenityContext, data_about_bot: &Ready) {
        if let Err(e) = self.register_commands(ctx.http()).await {
            error!("Failed to register commands: {e}");
        }

        if let Some(shard) = data_about_bot.shard {
            info!(
                "{} is connected on shard {}",
                data_about_bot.user.name, shard.id
            );

            SHARD_START_TIMES
                .write()
                .await
                .insert(shard.id, Instant::now());
        }

        ctx.set_activity(Some(ActivityData::watching(format!(
            "Anime | v{}",
            version()
        ))));
    }

    async fn handle_guild_join(&self, guild_id: GuildId) {
        info!("Joined guild: {}", guild_id);

        if let Err(e) = self.guild_service.add_guild(guild_id).await {
            error!("Failed to add guild: {e}");
        }
    }

    async fn handle_guild_leave(&self, guild_id: GuildId) {
        info!("Left guild: {}", guild_id);

        if let Err(e) = self.guild_service.remove_guild(guild_id).await {
            error!("Failed to remove guild: {e}");
        }
    }

    async fn register_commands(&self, http: &Http) -> Result<Vec<Command>, SerenityError> {
        match self.testing_guild {
            Some(testing_guild) => {
                testing_guild
                    .set_commands(http, &self.create_commands)
                    .await
            }
            None => Command::set_global_commands(http, &self.create_commands).await,
        }
    }
}

pub async fn pre_command(ctx: Context<'_>) {
    let data = ctx.data();

    if let Err(e) = data.user_service.add_user(ctx.author().id).await {
        error!("Failed to add user: {e}");
    }

    if let Some(guild_id) = ctx.guild_id()
        && let Err(e) = data.guild_service.add_guild(guild_id).await
    {
        error!("Failed to add guild: {e}");
    }

    log_command_invocation(ctx, ExecutionStatus::Running).await;
}

pub async fn post_command(ctx: Context<'_>) {
    log_command_completion(ctx, ExecutionStatus::Success).await;
}

async fn log_command_invocation(ctx: Context<'_>, status: ExecutionStatus) {
    let Context::Application(app_ctx) = ctx else {
        unreachable!()
    };

    let ctx_id = ctx.id();
    let guild_id = ctx.guild_id();
    let user_id = ctx.author().id;
    let command_name = ctx.invoked_command_name().to_string();
    let command_type = CommandType(app_ctx.interaction.data.kind);

    info!(
        "[COMMAND] [{:<18}] SHARD={} | GUILD={:<18} | USER={:<18} | TYPE={:<10} | CMD={}",
        ctx_id,
        ctx.serenity_context().shard_id,
        guild_id.unwrap_or_default(),
        user_id,
        command_type,
        ctx.invocation_string(),
    );

    let data = ctx.data();

    let res = match guild_id {
        Some(guild_id) => {
            data.metrics_service
                .add_guild_command_usage(
                    ctx_id,
                    user_id,
                    guild_id,
                    command_name,
                    command_type,
                    status,
                )
                .await
        }
        None => {
            data.metrics_service
                .add_private_command_usage(ctx_id, user_id, command_name, command_type, status)
                .await
        }
    };

    if let Err(e) = res {
        warn!("Failed to add command usage: {e}");
    }

    let start_time = Instant::now();
    ctx.set_invocation_data(start_time).await;
}

pub async fn log_command_completion(ctx: Context<'_>, status: ExecutionStatus) {
    let execution_time = get_execution_time(ctx).await;
    let ctx_id = ctx.id();

    info!(
        "[COMMAND] [{:<18}] STATUS={:<7} | TIME={}",
        ctx_id,
        status,
        format_duration(execution_time)
    );

    let data = ctx.data();

    let res = if ctx.guild_id().is_some() {
        data.metrics_service
            .update_guild_command_usage(ctx_id, status, execution_time.as_millis())
            .await
    } else {
        data.metrics_service
            .update_private_command_usage(ctx_id, status, execution_time.as_millis())
            .await
    };

    if let Err(e) = res {
        warn!("Failed to update command usage: {e}");
    }
}

async fn get_execution_time(ctx: Context<'_>) -> Duration {
    ctx.invocation_data::<Instant>()
        .await
        .as_deref()
        .map(|t| t.elapsed())
        .unwrap_or_default()
}
