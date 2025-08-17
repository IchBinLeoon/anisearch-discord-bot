use chrono::{Datelike, Utc};
use poise::{ChoiceParameter, CreateReply};

use crate::Context;
use crate::clients::anilist::media_query::{MediaSeason, MediaSort};
use crate::commands::search::anime::{create_media_buttons, create_media_embed};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;

#[derive(ChoiceParameter)]
enum SeasonChoice {
    Winter,
    Spring,
    Summer,
    Fall,
}

#[derive(ChoiceParameter)]
enum SortChoice {
    Popularity,
    Score,
    #[name = "Start Date"]
    StartDate,
    Title,
}

/// 📅 Display the currently airing anime or browse a selected season and year.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn seasonal(
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

    let season = season.map(|s| s.into()).unwrap_or(now.month().into());
    let year = year.unwrap_or(now.year());
    let sort = sort.unwrap_or(SortChoice::Popularity).into();

    let data = ctx.data();

    match data.anilist_service.seasonal(season, year, sort).await? {
        Some(anime) => {
            let pages = anime
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

impl From<SeasonChoice> for MediaSeason {
    fn from(value: SeasonChoice) -> Self {
        match value {
            SeasonChoice::Winter => MediaSeason::WINTER,
            SeasonChoice::Spring => MediaSeason::SPRING,
            SeasonChoice::Summer => MediaSeason::SUMMER,
            SeasonChoice::Fall => MediaSeason::FALL,
        }
    }
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

impl From<SortChoice> for MediaSort {
    fn from(value: SortChoice) -> Self {
        match value {
            SortChoice::Popularity => MediaSort::POPULARITY_DESC,
            SortChoice::Score => MediaSort::SCORE_DESC,
            SortChoice::StartDate => MediaSort::START_DATE,
            SortChoice::Title => MediaSort::TITLE_ROMAJI,
        }
    }
}
