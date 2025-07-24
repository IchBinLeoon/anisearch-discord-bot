use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed, FormattedTimestamp,
    FormattedTimestampStyle, Timestamp,
};

use crate::Context;
use crate::clients::anilist::media_query::{
    MediaFormat, MediaQueryPageMedia, MediaSource, MediaStatus, MediaType,
};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{
    UNKNOWN_EMBED_FIELD, convert_to_color, format_date, format_opt, sanitize_description,
};
use crate::utils::{ANILIST_EMOJI, MYANIMELIST_EMOJI};

/// 📺 Search for an anime and display detailed information.
#[poise::command(
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn anime(
    ctx: Context<'_>,
    #[description = "Title of the anime to search for."]
    #[autocomplete = "autocomplete_title"]
    title: String,
    #[description = "Maximum number of results to display."]
    #[min = 1]
    #[max = 15]
    limit: Option<usize>,
) -> Result<()> {
    ctx.defer().await?;

    let data = ctx.data();

    match data
        .anilist_service
        .search_anime(title.clone(), limit)
        .await?
    {
        Some(anime) => {
            let pages = anime
                .iter()
                .map(|data| {
                    Page::new(create_media_embed(data)).add_link_buttons(create_media_buttons(data))
                })
                .collect();

            let mut paginator = Paginator::builder().pages(pages).build();

            paginator.paginate(ctx).await?;
        }
        None => {
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None).description(
                format!("An anime with the title `{title}` could not be found."),
            );

            let reply = CreateReply::new().embed(embed);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}

async fn autocomplete_title<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    let data = ctx.data();

    let titles = data
        .anilist_service
        .anime_autocomplete(partial.trim().to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> =
        titles.into_iter().map(AutocompleteChoice::from).collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

pub fn create_media_embed(data: &MediaQueryPageMedia) -> CreateEmbed {
    let title = data
        .title
        .as_ref()
        .and_then(|t| {
            let romaji = t.romaji.as_ref()?;

            match &t.english {
                Some(english) if english != romaji => Some(format!("{romaji} ({english})")),
                _ => Some(romaji.to_string()),
            }
        })
        .unwrap_or(UNKNOWN_EMBED_FIELD.to_string());

    let mut embed = create_anilist_embed(
        title,
        Some(format_media_format(data.format.as_ref()).to_string()),
    );

    if let Some(desc) = &data.description {
        embed = embed.description(sanitize_description(desc, 400));
    }

    if let Some(cover) = &data.cover_image {
        if let Some(img) = &cover.large {
            embed = embed.thumbnail(img);
        }

        if let Some(color) = cover.color.as_ref().and_then(|c| convert_to_color(c)) {
            embed = embed.color(color);
        }
    }

    if let Some(img) = &data.banner_image {
        embed = embed.image(img);
    }

    if let Some(MediaType::ANIME) = data.type_ {
        let episodes: Option<String> = match (&data.status, &data.next_airing_episode) {
            (Some(MediaStatus::RELEASING), Some(next)) => {
                let count = match data.episodes {
                    Some(total) => format!("{}/{}", next.episode - 1, total),
                    None => (next.episode - 1).to_string(),
                };

                let timestamp = Timestamp::from_unix_timestamp(next.airing_at)
                    .map(|t| {
                        FormattedTimestamp::new(t, Some(FormattedTimestampStyle::RelativeTime))
                            .to_string()
                    })
                    .unwrap_or(UNKNOWN_EMBED_FIELD.to_string());

                Some(format!("{count} (Next {timestamp})"))
            }
            _ => data.episodes.map(|e| e.to_string()),
        };

        embed = embed.field("Episodes", format_opt(episodes), false);
    }

    if let Some(MediaType::MANGA) = data.type_ {
        embed = embed
            .field("Chapters", format_opt(data.chapters), true)
            .field("Volumes", format_opt(data.volumes), true)
            .field("Source", format_media_source(data.source.as_ref()), true);
    }

    let start_date = data.start_date.as_ref();
    let end_date = data.end_date.as_ref();

    embed = embed
        .field("Status", format_media_status(data.status.as_ref()), true)
        .field(
            "Start Date",
            format_date(
                start_date.and_then(|d| d.year),
                start_date.and_then(|d| d.month),
                start_date.and_then(|d| d.day),
            ),
            true,
        )
        .field(
            "End Date",
            format_date(
                end_date.and_then(|d| d.year),
                end_date.and_then(|d| d.month),
                end_date.and_then(|d| d.day),
            ),
            true,
        );

    if let Some(MediaType::ANIME) = data.type_ {
        let duration = data.duration.map(|d| format!("{d} mins"));

        let studio = data
            .studios
            .as_ref()
            .and_then(|s| s.nodes.as_ref()?.iter().flatten().next())
            .map(|s| s.name.as_str());

        embed = embed
            .field("Duration", format_opt(duration), true)
            .field("Studio", format_opt(studio), true)
            .field("Source", format_media_source(data.source.as_ref()), true);
    }

    embed = embed
        .field("Score", format_opt(data.mean_score), true)
        .field("Popularity", format_opt(data.popularity), true)
        .field("Favourites", format_opt(data.favourites), true);

    if let Some(genres) = &data.genres {
        let genres: Vec<String> = genres.iter().flatten().map(|g| format!("`{g}`")).collect();

        if !genres.is_empty() {
            embed = embed.field("Genres", genres.join(", "), false);
        }
    }

    embed
}

pub fn create_media_buttons(data: &MediaQueryPageMedia) -> Vec<CreateButton> {
    let media = match data.type_ {
        Some(MediaType::ANIME) => "anime",
        Some(MediaType::MANGA) => "manga",
        _ => unreachable!(),
    };

    let mut buttons = vec![
        CreateButton::new_link(format!("https://anilist.co/{media}/{}/", data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ];

    if let Some(id) = data.id_mal {
        buttons.push(
            CreateButton::new_link(format!("https://myanimelist.net/{media}/{id}/"))
                .label("MyAnimeList")
                .emoji(MYANIMELIST_EMOJI),
        )
    }

    buttons
}

fn format_media_format(format: Option<&MediaFormat>) -> &'static str {
    match format {
        Some(MediaFormat::TV) => "TV",
        Some(MediaFormat::TV_SHORT) => "TV Short",
        Some(MediaFormat::MOVIE) => "Movie",
        Some(MediaFormat::SPECIAL) => "Special",
        Some(MediaFormat::OVA) => "OVA",
        Some(MediaFormat::ONA) => "ONA",
        Some(MediaFormat::MUSIC) => "Music",
        Some(MediaFormat::MANGA) => "Manga",
        Some(MediaFormat::NOVEL) => "Novel",
        Some(MediaFormat::ONE_SHOT) => "One Shot",
        _ => UNKNOWN_EMBED_FIELD,
    }
}

fn format_media_status(status: Option<&MediaStatus>) -> &'static str {
    match status {
        Some(MediaStatus::FINISHED) => "Finished",
        Some(MediaStatus::RELEASING) => "Releasing",
        Some(MediaStatus::NOT_YET_RELEASED) => "Not Yet Released",
        Some(MediaStatus::CANCELLED) => "Cancelled",
        Some(MediaStatus::HIATUS) => "Hiatus",
        _ => UNKNOWN_EMBED_FIELD,
    }
}

fn format_media_source(source: Option<&MediaSource>) -> &'static str {
    match source {
        Some(MediaSource::ORIGINAL) => "Original",
        Some(MediaSource::MANGA) => "Manga",
        Some(MediaSource::LIGHT_NOVEL) => "Light Novel",
        Some(MediaSource::VISUAL_NOVEL) => "Visual Novel",
        Some(MediaSource::VIDEO_GAME) => "Video Game",
        Some(MediaSource::OTHER) => "Other",
        Some(MediaSource::NOVEL) => "Novel",
        Some(MediaSource::DOUJINSHI) => "Doujinshi",
        Some(MediaSource::ANIME) => "Anime",
        Some(MediaSource::WEB_NOVEL) => "Web Novel",
        Some(MediaSource::LIVE_ACTION) => "Live Action",
        Some(MediaSource::GAME) => "Game",
        Some(MediaSource::COMIC) => "Comic",
        Some(MediaSource::MULTIMEDIA_PROJECT) => "Multimedia Project",
        Some(MediaSource::PICTURE_BOOK) => "Picture Book",
        _ => UNKNOWN_EMBED_FIELD,
    }
}
