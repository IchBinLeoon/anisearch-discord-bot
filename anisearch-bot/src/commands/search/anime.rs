use poise::CreateReply;
use poise::serenity_prelude::{
    CreateButton, CreateEmbed, FormattedTimestamp, FormattedTimestampStyle, Timestamp,
};

use crate::clients::anilist::media_query::{
    MediaFormat, MediaQueryPageMedia, MediaSource, MediaStatus, MediaType,
};
use crate::commands::autocomplete::autocomplete_anime_title;
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{
    UNKNOWN_EMBED_FIELD, convert_to_color, format_date, format_opt, sanitize_description,
};
use crate::utils::{ANILIST_BASE_URL, ANILIST_EMOJI, MYANIMELIST_BASE_URL, MYANIMELIST_EMOJI};
use crate::{Context, anilist_media_url, myanimelist_media_url};

/// 📺 Search for an anime and display detailed information.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn anime(
    ctx: Context<'_>,
    #[description = "Title of the anime to search for."]
    #[autocomplete = autocomplete_anime_title]
    #[min_length = 1]
    #[max_length = 100]
    title: String,
    #[description = "Maximum number of results to display."]
    #[min = 1]
    #[max = 15]
    limit: Option<usize>,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

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

            let mut paginator = Paginator::builder()
                .pages(pages)
                .ephemeral(ephemeral)
                .build();

            paginator.paginate(ctx).await?;
        }
        None => {
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None, None).description(
                format!("An anime with the title `{title}` could not be found."),
            );

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}

pub fn create_media_embed(data: &MediaQueryPageMedia) -> CreateEmbed<'_> {
    let title = data
        .title
        .as_ref()
        .and_then(|t| format_title(t.romaji.as_ref(), t.english.as_ref()));

    let mut embed = create_anilist_embed(
        format_opt(title),
        Some(format_media_format(data.format.as_ref()).to_string()),
        Some(anilist_media_url!(MediaType, data.type_, data.id)),
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
        embed = add_episodes(embed, data);
    }

    if let Some(MediaType::MANGA) = data.type_ {
        embed = add_manga_fields(embed, data);
    }

    embed = add_common_fields(embed, data);

    if let Some(MediaType::ANIME) = data.type_ {
        embed = add_anime_fields(embed, data);
    }

    embed = add_stats_fields(embed, data);
    embed = add_genres(embed, data);

    embed
}

pub fn create_media_buttons(data: &MediaQueryPageMedia) -> Vec<CreateButton<'_>> {
    let mut buttons = vec![
        CreateButton::new_link(anilist_media_url!(MediaType, data.type_, data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ];

    if let Some(id) = data.id_mal {
        buttons.push(
            CreateButton::new_link(myanimelist_media_url!(MediaType, data.type_, id))
                .label("MyAnimeList")
                .emoji(MYANIMELIST_EMOJI),
        )
    }

    buttons
}

fn format_title(romaji: Option<&String>, english: Option<&String>) -> Option<String> {
    let romaji = romaji?;

    match english {
        Some(english) if english != romaji => Some(format!("{romaji} ({english})")),
        _ => Some(romaji.to_string()),
    }
}

fn add_episodes<'a>(embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    let episodes = format_episodes(data);

    embed.field("Episodes", format_opt(episodes), false)
}

fn format_episodes(data: &MediaQueryPageMedia) -> Option<String> {
    match (&data.status, &data.next_airing_episode) {
        (Some(MediaStatus::RELEASING), Some(next)) => {
            let current = next.episode - 1;

            let count = match data.episodes {
                Some(total) => format!("{current}/{total}"),
                None => current.to_string(),
            };

            let next_airing = format_opt(format_next_airing_time(next.airing_at));

            Some(format!("{count} (Next {next_airing})"))
        }
        _ => data.episodes.map(|e| e.to_string()),
    }
}

fn format_next_airing_time(airing_at: i64) -> Option<String> {
    Timestamp::from_unix_timestamp(airing_at)
        .map(|t| {
            FormattedTimestamp::new(t, Some(FormattedTimestampStyle::RelativeTime)).to_string()
        })
        .ok()
}

fn add_manga_fields<'a>(embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    embed
        .field("Chapters", format_opt(data.chapters), true)
        .field("Volumes", format_opt(data.volumes), true)
        .field("Source", format_media_source(data.source.as_ref()), true)
}

fn add_common_fields<'a>(embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    let start_date = data.start_date.as_ref();
    let end_date = data.end_date.as_ref();

    embed
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
        )
}

fn add_anime_fields<'a>(embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    let duration = data.duration.map(|d| format!("{d} mins"));

    let studio = data
        .studios
        .as_ref()
        .and_then(|s| s.nodes.as_ref()?.iter().flatten().next())
        .map(|s| s.name.clone());

    embed
        .field("Duration", format_opt(duration), true)
        .field("Studio", format_opt(studio), true)
        .field("Source", format_media_source(data.source.as_ref()), true)
}

fn add_stats_fields<'a>(embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    embed
        .field("Score", format_opt(data.mean_score), true)
        .field("Popularity", format_opt(data.popularity), true)
        .field("Favourites", format_opt(data.favourites), true)
}

fn add_genres<'a>(mut embed: CreateEmbed<'a>, data: &MediaQueryPageMedia) -> CreateEmbed<'a> {
    if let Some(genres) = extract_genres(data) {
        embed = embed.field("Genres", genres.join(", "), false);
    }

    embed
}

fn extract_genres(data: &MediaQueryPageMedia) -> Option<Vec<String>> {
    let genres: Vec<String> = data
        .genres
        .as_ref()?
        .iter()
        .flatten()
        .map(|g| format!("`{g}`"))
        .collect();

    if genres.is_empty() {
        None
    } else {
        Some(genres)
    }
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
