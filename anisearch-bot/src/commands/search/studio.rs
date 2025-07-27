use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::clients::anilist::studio_query::{
    MediaFormat, MediaType, StudioQueryPageStudios, StudioQueryPageStudiosMedia,
    StudioQueryPageStudiosMediaNodes,
};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{UNKNOWN_EMBED_FIELD, format_opt};
use crate::utils::{ANILIST_BASE_URL, ANILIST_EMOJI};
use crate::{Context, anilist_media_url, anilist_studio_url};

/// 🏢 Search for a studio and display detailed information.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn studio(
    ctx: Context<'_>,
    #[description = "Name of the studio to search for."]
    #[autocomplete = "autocomplete_name"]
    name: String,
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
        .search_studio(name.clone(), limit)
        .await?
    {
        Some(studios) => {
            let pages = studios
                .iter()
                .map(|data| {
                    Page::new(create_studio_embed(data))
                        .add_link_buttons(create_studio_buttons(data))
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
                format!("A studio with the name `{name}` could not be found."),
            );

            let reply = CreateReply::new().embed(embed).ephemeral(ephemeral);

            ctx.send(reply).await?;
        }
    }

    Ok(())
}

async fn autocomplete_name<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    let data = ctx.data();

    let names = data
        .anilist_service
        .studios_autocomplete(partial.trim().to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> =
        names.into_iter().map(AutocompleteChoice::from).collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

fn create_studio_embed(data: &StudioQueryPageStudios) -> CreateEmbed {
    let mut embed = create_anilist_embed(
        data.name.to_string(),
        Some("Studio".to_string()),
        Some(anilist_studio_url!(data.id)),
    );

    if data.is_animation_studio {
        embed = embed.description("**Animation Studio**".to_string())
    }

    embed = add_productions(embed, data);

    embed
}

fn create_studio_buttons(data: &StudioQueryPageStudios) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(anilist_studio_url!(data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
}

fn add_productions<'a>(
    mut embed: CreateEmbed<'a>,
    data: &'a StudioQueryPageStudios,
) -> CreateEmbed<'a> {
    if let Some(media) = &data.media {
        if let Some(img) = extract_image(media) {
            embed = embed.thumbnail(img);
        }

        if let Some(productions) = extract_productions(media) {
            embed = embed.field("Most Popular Productions", productions.join("\n"), false);
        }
    }

    embed
}

fn extract_image(media: &StudioQueryPageStudiosMedia) -> Option<&String> {
    media
        .nodes
        .as_ref()?
        .iter()
        .flatten()
        .find(|m| !m.is_adult.unwrap_or_default())
        .and_then(|m| m.cover_image.as_ref()?.large.as_ref())
}

fn extract_productions(media: &StudioQueryPageStudiosMedia) -> Option<Vec<String>> {
    let nodes = media.nodes.as_ref()?;

    let productions: Vec<String> = nodes
        .iter()
        .flatten()
        .filter(|m| !m.is_adult.unwrap_or_default())
        .filter_map(format_production)
        .collect();

    if productions.is_empty() {
        None
    } else {
        Some(productions)
    }
}

fn format_production(media: &StudioQueryPageStudiosMediaNodes) -> Option<String> {
    let title = media.title.as_ref()?.romaji.as_ref()?;
    let url = anilist_media_url!(MediaType, media.type_, media.id);
    let format = format_media_format(media.format.as_ref());
    let episodes = format_opt(media.episodes);

    Some(format!(
        "[{title}]({url}) » **{format}** • Episodes: **{episodes}**"
    ))
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
