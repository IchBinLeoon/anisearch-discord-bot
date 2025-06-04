use chrono::Utc;
use poise::serenity_prelude::{Color, CreateEmbed, CreateEmbedFooter};

use crate::Context;

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
