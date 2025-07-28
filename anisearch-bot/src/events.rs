use poise::async_trait;
use poise::serenity_prelude::{
    CacheHttp, Command, Context as SerenityContext, CreateCommand, EventHandler, FullEvent, GuildId,
};
use strum::Display;
use tokio::time::Instant;
use tracing::{error, info};

use crate::Context;

pub struct Handler {
    pub create_commands: Vec<CreateCommand<'static>>,
    pub testing_guild: Option<GuildId>,
}

#[async_trait]
impl EventHandler for Handler {
    async fn dispatch(&self, ctx: &SerenityContext, event: &FullEvent) {
        match event {
            FullEvent::Ready { data_about_bot, .. } => {
                if let Some(testing_guild) = self.testing_guild {
                    if let Err(e) = testing_guild
                        .set_commands(ctx.http(), &self.create_commands)
                        .await
                    {
                        error!("Failed to set testing guild commands: {e}");
                    }
                } else if let Err(e) =
                    Command::set_global_commands(ctx.http(), &self.create_commands).await
                {
                    error!("Failed to set global commands: {e}");
                }

                if let Some(shard) = data_about_bot.shard {
                    info!(
                        "{} is connected on shard {}",
                        data_about_bot.user.name, shard.id
                    );
                } else {
                    info!("{} is connected", data_about_bot.user.name);
                }
            }
            FullEvent::GuildCreate { guild, is_new, .. } => {
                if matches!(is_new, Some(true)) {
                    info!("Joined guild: {}", guild.id);
                }
            }
            FullEvent::GuildDelete { incomplete, .. } => {
                info!("Left guild: {}", incomplete.id);
            }
            _ => {}
        }
    }
}

pub async fn pre_command(ctx: Context<'_>) {
    let Context::Application(app_ctx) = ctx else {
        unreachable!()
    };

    info!(
        "[COMMAND] [{:<18}] CONTEXT={} | SHARD={} | GUILD={:<18} | CHANNEL={:<18} | USER={:<18} | TYPE={} | CMD={}",
        ctx.id(),
        app_ctx.interaction.context.map(|c| c.0).unwrap_or_default(),
        ctx.serenity_context().shard_id,
        ctx.guild_id().unwrap_or_default(),
        ctx.channel_id(),
        ctx.author().id,
        app_ctx.interaction.data.kind.0,
        ctx.invocation_string(),
    );

    let start_time = Instant::now();
    ctx.set_invocation_data(start_time).await;
}

pub async fn post_command(ctx: Context<'_>) {
    log_command_completion(
        ctx.id(),
        CommandExecutionStatus::Success,
        get_execution_time(ctx).await,
    );
}

pub fn log_command_completion(ctx_id: u64, status: CommandExecutionStatus, execution_time: u128) {
    info!(
        "[COMMAND] [{:<18}] STATUS={} | TIME={}ms",
        ctx_id, status, execution_time
    );
}

#[derive(Display)]
#[strum(serialize_all = "UPPERCASE")]
pub enum CommandExecutionStatus {
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
