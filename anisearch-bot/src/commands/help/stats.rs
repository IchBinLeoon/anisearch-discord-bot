use anisearch_lib::{BOT_INVITE, GITHUB_URL, SERVER_INVITE, WEBSITE_URL, version};
use poise::CreateReply;
use poise::serenity_prelude::{CreateActionRow, CreateButton, CreateComponent, Mentionable};

use crate::Context;
use crate::error::Result;
use crate::events::SHARD_START_TIMES;
use crate::utils::CREATOR;
use crate::utils::embeds::create_default_embed;
use crate::utils::format::{NO_ANSWER_EMBED_FIELD, format_duration_secs};

/// 📊 Display information and statistics about the bot.
#[poise::command(
    slash_command,
    rename = "stats",
    category = "Help",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn stats_slash_command(ctx: Context<'_>) -> Result<()> {
    let data = ctx.data();
    let cache = ctx.cache();

    let user_count = data.metrics_service.get_user_count().await?;
    let commands_used_count = data.metrics_service.get_commands_used_count().await?;

    let shard_id = ctx.serenity_context().shard_id;
    let uptime = SHARD_START_TIMES
        .read()
        .await
        .get(&shard_id)
        .map_or(NO_ANSWER_EMBED_FIELD.to_string(), |i| {
            format_duration_secs(i.elapsed())
        });

    let embed = create_default_embed(ctx)
        .await
        .title("📊 Information & Statistics")
        .description(format!(
            "**Shard:** {}\n**Uptime:** {}\n**Version:** v{}\n**Creator:** {}",
            shard_id,
            uptime,
            version(),
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
