use anisearch_lib::BOT_INVITE;
use poise::CreateReply;
use poise::serenity_prelude::{CreateActionRow, CreateButton, CreateComponent};

use crate::Context;
use crate::error::Result;
use crate::utils::embeds::create_default_embed;

/// 🔗 Invite the bot to your server.
#[poise::command(
    slash_command,
    rename = "invite",
    category = "Help",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn invite_slash_command(ctx: Context<'_>) -> Result<()> {
    let embed = create_default_embed(ctx)
        .await
        .title("🔗 Invite AniSearch")
        .description("Thanks for your interest! ❤️");

    let buttons = [CreateButton::new_link(BOT_INVITE)
        .label("Invite AniSearch to Your Server")
        .emoji('🔗')];

    let components = [CreateComponent::ActionRow(CreateActionRow::buttons(
        &buttons,
    ))];

    let reply = CreateReply::new().embed(embed).components(&components);

    ctx.send(reply).await?;

    Ok(())
}
