use poise::CreateReply;

use crate::utils::embeds::create_default_embed;
use crate::{Context, Error};

/// 🏓 Check the latency of the bot.
#[poise::command(
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn ping(ctx: Context<'_>) -> Result<(), Error> {
    ctx.defer().await?;

    let embed = create_default_embed(ctx).await.title("🏓 Pong!");

    let reply = CreateReply::new().embed(embed);

    ctx.send(reply).await?;

    Ok(())
}
