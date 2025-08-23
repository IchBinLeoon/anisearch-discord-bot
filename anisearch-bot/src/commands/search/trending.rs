use poise::CreateReply;

use crate::Context;
use crate::commands::choices::MediaChoice;
use crate::commands::search::anime::{create_media_buttons, create_media_embed};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;

/// 🔥 Display the currently trending anime or manga.
#[poise::command(
    slash_command,
    rename = "trending",
    category = "Search",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn trending_slash_command(
    ctx: Context<'_>,
    #[description = "Type of media."] media: MediaChoice,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

    let data = ctx.data();

    match data.anilist_service.trending(media.into()).await? {
        Some(trending) => {
            let pages = trending
                .iter()
                .map(|data| {
                    Page::new(create_media_embed(data)).add_link_buttons(create_media_buttons(data))
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
                .description("Trending media could not be found.");

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}
