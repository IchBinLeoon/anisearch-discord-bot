use poise::async_trait;
use poise::serenity_prelude::{
    CacheHttp, Command, Context, CreateCommand, EventHandler, FullEvent, GuildId,
};
use tracing::{error, info};

pub struct Handler {
    pub create_commands: Vec<CreateCommand<'static>>,
    pub testing_guild: Option<GuildId>,
}

#[async_trait]
impl EventHandler for Handler {
    async fn dispatch(&self, ctx: &Context, event: &FullEvent) {
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
