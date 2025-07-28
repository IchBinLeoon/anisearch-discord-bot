use poise::async_trait;
use poise::serenity_prelude::{
    CacheHttp, Command, Context as SerenityContext, CreateCommand, EventHandler, FullEvent,
    GuildId, Ready,
};
use std::sync::Arc;
use strum::Display;
use tokio::time::Instant;
use tracing::{error, info};

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
        let res = match self.testing_guild {
            Some(testing_guild) => {
                testing_guild
                    .set_commands(ctx.http(), &self.create_commands)
                    .await
            }
            None => Command::set_global_commands(ctx.http(), &self.create_commands).await,
        };

        if let Err(e) = res {
            error!("Failed to set commands: {e}");
        }

        info!(
            "{} is connected on shard {}",
            data_about_bot.user.name,
            data_about_bot.shard.unwrap().id
        );
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
}

pub async fn pre_command(ctx: Context<'_>) {
    let Context::Application(app_ctx) = ctx else {
        unreachable!()
    };

    let ctx_id = ctx.id();

    let shard_id = ctx.serenity_context().shard_id;
    let guild_id = ctx.guild_id();
    let channel_id = ctx.channel_id();
    let user_id = ctx.author().id;

    let command_name = ctx.invoked_command_name().to_string();
    let command_type = app_ctx.interaction.data.kind.0;
    let invocation_string = ctx.invocation_string();

    info!(
        "[COMMAND] [{:<18}] SHARD={} | GUILD={:<18} | CHANNEL={:<18} | USER={:<18} | TYPE={} | CMD={}",
        ctx_id,
        shard_id,
        guild_id.unwrap_or_default(),
        channel_id,
        user_id,
        command_type,
        invocation_string,
    );

    let data = ctx.data();

    let res = match guild_id {
        Some(guild_id) => {
            data.user_service
                .add_guild_command_usage(ctx_id, user_id, guild_id, command_name)
                .await
        }
        None => {
            data.user_service
                .add_private_command_usage(ctx_id, user_id, command_name)
                .await
        }
    };

    if let Err(e) = res {
        error!("Failed to log command usage: {e}");
    }

    let start_time = Instant::now();
    ctx.set_invocation_data(start_time).await;
}

pub async fn post_command(ctx: Context<'_>) {
    log_command_completion(
        ctx.id(),
        ExecutionStatus::Success,
        get_execution_time(ctx).await,
    );
}

pub fn log_command_completion(ctx_id: u64, status: ExecutionStatus, execution_time: u128) {
    info!(
        "[COMMAND] [{:<18}] STATUS={} | TIME={}ms",
        ctx_id, status, execution_time
    );
}

#[derive(Display)]
#[strum(serialize_all = "UPPERCASE")]
pub enum ExecutionStatus {
    Success,
    Error,
}

pub async fn get_execution_time(ctx: Context<'_>) -> u128 {
    ctx.invocation_data::<Instant>()
        .await
        .as_deref()
        .map(|t| t.elapsed().as_millis())
        .unwrap_or_default()
}
