use poise::CreateReply;

use crate::Context;
use crate::error::Result;
use crate::utils::embeds::create_default_embed;

/// 🏓 Check the latency of the bot.
#[poise::command(
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn ping(ctx: Context<'_>) -> Result<()> {
    ctx.defer().await?;

    let embed = create_default_embed(ctx).await.title("🏓 Pong!");

    let reply = CreateReply::new().embed(embed);

    ctx.send(reply).await?;

    Ok(())
}
