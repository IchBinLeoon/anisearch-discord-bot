use anisearch_lib::SERVER_INVITE;
use poise::CreateReply;
use poise::serenity_prelude::{CreateActionRow, CreateButton, CreateComponent};

use crate::Context;
use crate::error::Result;
use crate::utils::embeds::create_default_embed;

/// 🤝 Join the bot support server.
#[poise::command(
    category = "Help",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn support(ctx: Context<'_>) -> Result<()> {
    let embed = create_default_embed(ctx)
        .await
        .title("🤝 Support Server")
        .description("Head to the support server! 🛡️");

    let buttons = [CreateButton::new_link(SERVER_INVITE)
        .label("Join the Support Server")
        .emoji('🤝')];

    let components = [CreateComponent::ActionRow(CreateActionRow::buttons(
        &buttons,
    ))];

    let reply = CreateReply::new().embed(embed).components(&components);

    ctx.send(reply).await?;

    Ok(())
}
