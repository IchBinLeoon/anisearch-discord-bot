use chrono::Utc;
use poise::serenity_prelude::{Color, CreateEmbed, CreateEmbedAuthor, CreateEmbedFooter};

use crate::Context;
use crate::utils::ANILIST_LOGO;

pub const EMBED_DEFAULT_COLOUR: Color = Color::from_rgb(65, 105, 225);
pub const EMBED_ERROR_COLOUR: Color = Color::from_rgb(255, 0, 0);

pub async fn create_default_embed(ctx: Context<'_>) -> CreateEmbed {
    let (display_name, icon_url) = match ctx.author_member().await {
        Some(author) => (author.display_name().to_string(), author.face()),
        None => (ctx.author().display_name().to_string(), ctx.author().face()),
    };

    let footer = CreateEmbedFooter::new(display_name).icon_url(icon_url);

    CreateEmbed::new()
        .color(EMBED_DEFAULT_COLOUR)
        .timestamp(Utc::now())
        .footer(footer)
}

pub async fn create_error_embed(ctx: Context<'_>) -> CreateEmbed {
    create_default_embed(ctx).await.color(EMBED_ERROR_COLOUR)
}

pub fn create_anilist_embed<'a>(title: String, name: Option<String>) -> CreateEmbed<'a> {
    let footer = CreateEmbedFooter::new("Provided by https://anilist.co/").icon_url(ANILIST_LOGO);

    let mut embed = CreateEmbed::new()
        .title(title)
        .color(EMBED_DEFAULT_COLOUR)
        .footer(footer);

    if let Some(name) = name {
        embed = embed.author(CreateEmbedAuthor::new(name).icon_url(ANILIST_LOGO))
    }

    embed
}
