use poise::serenity_prelude::{CreateEmbed, CreateEmbedAuthor};
use poise::{ChoiceParameter, CreateReply};
use strum::Display;

use crate::Context;
use crate::clients::anilist::media_query::MediaQueryPageMedia;
use crate::commands::search::anime::{
    create_media_buttons, create_media_embed, format_media_format,
};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_LOGO;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;

/// 🔥 Display the currently trending anime or manga.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn trending(
    ctx: Context<'_>,
    #[description = "Type of media."] media: MediaChoice,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

    let data = ctx.data();

    let trending = match media {
        MediaChoice::Anime => data.anilist_service.trending_anime().await?,
        MediaChoice::Manga => data.anilist_service.trending_manga().await?,
    };

    match trending {
        Some(trending) => {
            let pages = trending
                .iter()
                .enumerate()
                .map(|(index, data)| {
                    Page::new(create_trending_embed(data, index, media.clone()))
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
                .description(format!("Trending `{media}` could not be found."));

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}

#[derive(Clone, Display, ChoiceParameter)]
enum MediaChoice {
    Anime,
    Manga,
}

fn create_trending_embed(
    data: &MediaQueryPageMedia,
    index: usize,
    media: MediaChoice,
) -> CreateEmbed {
    let embed = create_media_embed(data);

    let author = CreateEmbedAuthor::new(format!(
        "{} • #{} Trending {}",
        format_media_format(data.format.as_ref()),
        index + 1,
        media
    ))
    .icon_url(ANILIST_LOGO);

    embed.author(author)
}
