use cruet::Inflector;
use poise::CreateReply;

use crate::Context;
use crate::error::Result;
use crate::utils::embeds::create_default_embed;

/// 🏓 Check the latency of the bot.
#[poise::command(
    category = "Help",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn ping(ctx: Context<'_>) -> Result<()> {
    let shards = ctx
        .serenity_context()
        .runners
        .iter()
        .map(|s| {
            let (id, (info, _)) = s.pair();

            let latency = info
                .latency
                .map_or("N/A".to_string(), |d| format!("{}ms", d.as_millis()));

            let stage = info.stage.to_string().to_title_case();

            format!("[SHARD #{id}] {latency:>5} {stage}")
        })
        .collect::<Vec<String>>();

    let embed = create_default_embed(ctx)
        .await
        .title("🏓 Pong!")
        .description(format!("```ini\n{}\n```", shards.join("\n")));

    let reply = CreateReply::new().embed(embed);

    ctx.send(reply).await?;

    Ok(())
}
