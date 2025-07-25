use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::Context;
use crate::clients::anilist::studio_query::MediaFormat;
use crate::clients::anilist::studio_query::StudioQueryPageStudios;
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_EMOJI;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{UNKNOWN_EMBED_FIELD, format_opt};

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
    let ephemeral = ephemeral.unwrap_or_default();

    if ephemeral {
        ctx.defer_ephemeral().await?;
    } else {
        ctx.defer().await?;
    }

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
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None).description(
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
    let mut embed = create_anilist_embed(data.name.to_string(), Some("Studio".to_string()));

    if data.is_animation_studio {
        embed = embed.description("**Animation Studio**".to_string())
    }

    if let Some(media) = &data.media {
        if let Some(img) = media.nodes.as_ref().and_then(|n| {
            n.iter()
                .flatten()
                .find(|m| !m.is_adult.unwrap_or(false))
                .and_then(|m| m.cover_image.as_ref()?.large.as_ref())
        }) {
            embed = embed.thumbnail(img);
        }

        let productions: Vec<String> = media
            .nodes
            .as_ref()
            .map(|n| {
                n.iter()
                    .flatten()
                    .filter(|m| !m.is_adult.unwrap_or(false))
                    .filter_map(|m| {
                        let title = m.title.as_ref()?.romaji.as_ref()?;

                        Some(format!(
                            "{title} » **{}** • Episodes: **{}**",
                            format_media_format(m.format.as_ref()),
                            format_opt(m.episodes)
                        ))
                    })
                    .collect()
            })
            .unwrap_or_default();

        if !productions.is_empty() {
            embed = embed.field("Most Popular Productions", productions.join("\n"), false);
        }
    }

    embed
}

fn create_studio_buttons(data: &StudioQueryPageStudios) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(format!("https://anilist.co/studio/{}/", data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
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
