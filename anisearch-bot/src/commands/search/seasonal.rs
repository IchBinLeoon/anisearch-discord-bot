use chrono::{Datelike, Utc};
use poise::CreateReply;
use poise::serenity_prelude::{CreateEmbed, CreateEmbedAuthor};

use crate::Context;
use crate::clients::anilist::media_query::{MediaQueryPageMedia, MediaSeason};
use crate::commands::search::anime::{
    create_media_buttons, create_media_embed, format_media_format,
};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_LOGO;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{UNKNOWN_EMBED_FIELD, format_opt};

/// 📅 Display the currently airing seasonal anime.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn seasonal(
    ctx: Context<'_>,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

    let now = Utc::now();

    let data = ctx.data();

    match data
        .anilist_service
        .seasonal_anime(now.month().into(), now.year())
        .await?
    {
        Some(anime) => {
            let pages = anime
                .iter()
                .map(|data| {
                    Page::new(create_seasonal_embed(data))
                        .add_link_buttons(create_media_buttons(data))
                })
                .collect();

            let mut paginator = Paginator::builder()
                .pages(pages)
                .ephemeral(ephemeral)
                .build();

            paginator.paginate(ctx).await?;
        }
        None => {
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None, None)
                .description("Seasonal anime could not be found.");

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}

fn create_seasonal_embed(data: &MediaQueryPageMedia) -> CreateEmbed {
    let embed = create_media_embed(data);

    let author = CreateEmbedAuthor::new(format!(
        "{} • {} {}",
        format_media_format(data.format.as_ref()),
        format_media_season(data.season.as_ref()),
        format_opt(data.season_year),
    ))
    .icon_url(ANILIST_LOGO);

    embed.author(author)
}

impl From<u32> for MediaSeason {
    fn from(value: u32) -> Self {
        match value {
            1..=3 => MediaSeason::WINTER,
            4..=6 => MediaSeason::SPRING,
            7..=9 => MediaSeason::SUMMER,
            10..=12 => MediaSeason::FALL,
            _ => unreachable!(),
        }
    }
}

fn format_media_season(format: Option<&MediaSeason>) -> &'static str {
    match format {
        Some(MediaSeason::WINTER) => "Winter",
        Some(MediaSeason::SPRING) => "Spring",
        Some(MediaSeason::SUMMER) => "Summer",
        Some(MediaSeason::FALL) => "Fall",
        _ => UNKNOWN_EMBED_FIELD,
    }
}
