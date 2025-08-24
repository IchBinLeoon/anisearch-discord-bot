use chrono::{Datelike, Utc};
use poise::CreateReply;

use crate::Context;
use crate::commands::choices::{SeasonChoice, SortChoice};
use crate::commands::search::anime::{create_media_buttons, create_media_embed};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;

/// 📅 Display the currently airing anime or browse a selected season and year.
#[poise::command(
    slash_command,
    rename = "seasonal",
    category = "Search",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn seasonal_slash_command(
    ctx: Context<'_>,
    #[description = "Season to display anime from."] season: Option<SeasonChoice>,
    #[description = "Year to display anime from."]
    #[min = 1900]
    #[max = 2100]
    year: Option<i32>,
    #[description = "Sort order of the results."] sort: Option<SortChoice>,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

    let now = Utc::now();

    let season = season.map_or(now.into(), Into::into);
    let year = year.unwrap_or(now.year());
    let sort = sort.unwrap_or_default().into();

    let data = ctx.data();

    match data.anilist_service.seasonal(season, year, sort).await? {
        Some(seasonal) => {
            let pages = seasonal
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
                .description("Seasonal anime could not be found.");

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}
