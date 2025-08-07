use poise::async_trait;
use poise::serenity_prelude::{
    CacheHttp, Command, Context as SerenityContext, CreateCommand, Error as SerenityError,
    EventHandler, FullEvent, GuildId, Http, Ready,
};
use std::sync::Arc;
use strum::Display;
use tokio::time::Instant;
use tracing::{error, info, warn};

use crate::Context;
use crate::services::guild::GuildService;

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
        }
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

    if let Some(guild_id) = ctx.guild_id() {
        if let Err(e) = data.guild_service.add_guild(guild_id).await {
            error!("Failed to add guild: {e}");
        }
    }

    log_command_invocation(ctx).await;
}

pub async fn post_command(ctx: Context<'_>) {
    log_command_completion(ctx, ExecutionStatus::Success).await;
}

async fn log_command_invocation(ctx: Context<'_>) {
    let Context::Application(app_ctx) = ctx else {
        unreachable!()
    };

    let ctx_id = ctx.id();
    let guild_id = ctx.guild_id();
    let user_id = ctx.author().id;
    let command_name = ctx.invoked_command_name().to_string();

    info!(
        "[COMMAND] [{:<18}] SHARD={} | GUILD={:<18} | CHANNEL={:<18} | USER={:<18} | TYPE={} | CMD={}",
        ctx_id,
        ctx.serenity_context().shard_id,
        guild_id.unwrap_or_default(),
        ctx.channel_id(),
        user_id,
        app_ctx.interaction.data.kind.0,
        ctx.invocation_string(),
    );

    let data = ctx.data();

    let res = match guild_id {
        Some(guild_id) => {
            data.metrics_service
                .add_guild_command_usage(ctx_id, user_id, guild_id, command_name)
                .await
        }
        None => {
            data.metrics_service
                .add_private_command_usage(ctx_id, user_id, command_name)
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

    info!(
        "[COMMAND] [{:<18}] STATUS={} | TIME={}ms",
        ctx.id(),
        status,
        execution_time
    );
}

#[derive(Display)]
#[strum(serialize_all = "UPPERCASE")]
pub enum ExecutionStatus {
    Success,
    Error,
}

async fn get_execution_time(ctx: Context<'_>) -> u128 {
    ctx.invocation_data::<Instant>()
        .await
        .as_deref()
        .map(|t| t.elapsed().as_millis())
        .unwrap_or_default()
}
