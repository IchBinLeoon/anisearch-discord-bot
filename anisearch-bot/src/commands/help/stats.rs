use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

use anisearch_lib::{BOT_INVITE, GITHUB_URL, SERVER_INVITE, WEBSITE_URL, version};
use chrono::Utc;
use humantime::format_duration;
use poise::CreateReply;
use poise::serenity_prelude::{CreateActionRow, CreateButton, CreateComponent, Mentionable};

use crate::Context;
use crate::error::Result;
use crate::events::START_TIME;
use crate::utils::CREATOR;
use crate::utils::embeds::create_default_embed;

/// 📊 Display information and statistics about the bot.
#[poise::command(
    category = "stats",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn stats(ctx: Context<'_>) -> Result<()> {
    let data = ctx.data();
    let cache = ctx.cache();

    let user_count = data.metrics_service.get_user_count().await?;
    let commands_used_count = data.metrics_service.get_commands_used_count().await?;

    let uptime = Duration::from_secs(
        Utc::now().timestamp() as u64 - AtomicU64::load(&START_TIME, Ordering::Relaxed),
    );

    let embed = create_default_embed(ctx)
        .await
        .title("📊 Information & Statistics")
        .description(format!(
            "**Version:** v{}\n**Uptime:** {}\n**Creator:** {}",
            version(),
            format_duration(uptime),
            CREATOR.mention()
        ))
        .thumbnail(ctx.cache().current_user().face())
        .field("❯ Servers", format!("` {} `", cache.guild_count()), true)
        .field("❯ Users", format!("` {} `", user_count), true)
        .field("❯ Shards", format!("` {} `", cache.shard_count()), true)
        .field(
            "❯ Commands Used",
            format!("` {} `", commands_used_count),
            false,
        );

    let buttons_upper = [
        CreateButton::new_link(BOT_INVITE)
            .label("Invite AniSearch")
            .emoji('🔗'),
        CreateButton::new_link(SERVER_INVITE)
            .label("Support Server")
            .emoji('🤝'),
    ];

    let buttons_lower = [
        CreateButton::new_link(WEBSITE_URL)
            .label("Website")
            .emoji('🌐'),
        CreateButton::new_link(GITHUB_URL)
            .label("GitHub")
            .emoji('🐙'),
    ];

    let components = [
        CreateComponent::ActionRow(CreateActionRow::buttons(&buttons_upper)),
        CreateComponent::ActionRow(CreateActionRow::buttons(&buttons_lower)),
    ];

    let reply = CreateReply::new().embed(embed).components(&components);

    ctx.send(reply).await?;

    Ok(())
}
