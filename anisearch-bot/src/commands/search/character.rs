use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::clients::anilist::character_query::{CharacterQueryPageCharacters, MediaType};
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{format_date, format_opt, sanitize_description};
use crate::utils::{ANILIST_BASE_URL, ANILIST_EMOJI};
use crate::{Context, anilist_character_url, anilist_media_url};

/// 🎭 Search for a character and display detailed information.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn character(
    ctx: Context<'_>,
    #[description = "Name of the character to search for."]
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
        .search_character(name.clone(), limit)
        .await?
    {
        Some(characters) => {
            let pages = characters
                .iter()
                .map(|data| {
                    Page::new(create_character_embed(data))
                        .add_link_buttons(create_character_buttons(data))
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
                format!("A character with the name `{name}` could not be found."),
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
        .character_autocomplete(partial.trim().to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> =
        names.into_iter().map(AutocompleteChoice::from).collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

fn create_character_embed(data: &CharacterQueryPageCharacters) -> CreateEmbed {
    let title = data
        .name
        .as_ref()
        .and_then(|n| format_name(n.full.as_ref(), n.native.as_ref()));

    let mut embed = create_anilist_embed(
        format_opt(title),
        Some("Character".to_string()),
        Some(anilist_character_url!(data.id)),
    );

    if let Some(desc) = &data.description {
        embed = embed.description(sanitize_description(desc, 1000));
    }

    if let Some(img) = data.image.as_ref().and_then(|i| i.large.as_ref()) {
        embed = embed.thumbnail(img);
    }

    embed = add_basic_fields(embed, data);
    embed = add_synonyms(embed, data);
    embed = add_appearances(embed, data);

    embed
}

fn create_character_buttons(data: &CharacterQueryPageCharacters) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(anilist_character_url!(data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
}

pub fn format_name(full: Option<&String>, native: Option<&String>) -> Option<String> {
    match (full, native) {
        (Some(full), Some(native)) => {
            if full == native {
                Some(full.to_string())
            } else {
                Some(format!("{full} ({native})"))
            }
        }
        (Some(full), None) => Some(full.to_string()),
        (None, Some(native)) => Some(native.to_string()),
        _ => None,
    }
}

fn add_basic_fields<'a>(
    embed: CreateEmbed<'a>,
    data: &CharacterQueryPageCharacters,
) -> CreateEmbed<'a> {
    let birthday = data.date_of_birth.as_ref();

    embed
        .field(
            "Birthday",
            format_date(
                birthday.and_then(|d| d.year),
                birthday.and_then(|d| d.month),
                birthday.and_then(|d| d.day),
            ),
            true,
        )
        .field("Age", format_opt(data.age.as_ref()), true)
        .field("Gender", format_opt(data.gender.as_ref()), true)
}

fn add_synonyms<'a>(
    mut embed: CreateEmbed<'a>,
    data: &CharacterQueryPageCharacters,
) -> CreateEmbed<'a> {
    if let Some(synonyms) = extract_synonyms(data) {
        embed = embed.field("Synonyms", synonyms.join(", "), false);
    }

    embed
}

fn extract_synonyms(data: &CharacterQueryPageCharacters) -> Option<Vec<String>> {
    let name = data.name.as_ref()?;

    let mut synonyms = vec![];

    if let Some(alt) = &name.alternative {
        synonyms.extend(alt.iter().flatten().map(|n| format!("`{n}`")));
    }

    if let Some(alt_spoiler) = &name.alternative_spoiler {
        synonyms.extend(alt_spoiler.iter().flatten().map(|n| format!("||`{n}`||")));
    }

    if synonyms.is_empty() {
        None
    } else {
        Some(synonyms)
    }
}

fn add_appearances<'a>(
    mut embed: CreateEmbed<'a>,
    data: &CharacterQueryPageCharacters,
) -> CreateEmbed<'a> {
    if let Some(appearances) = extract_appearances(data) {
        embed = embed.field("Popular Appearances", appearances.join(" • "), false);
    }

    embed
}

fn extract_appearances(data: &CharacterQueryPageCharacters) -> Option<Vec<String>> {
    let media = data.media.as_ref()?;
    let nodes = media.nodes.as_ref()?;

    let appearances: Vec<String> = nodes
        .iter()
        .flatten()
        .filter(|m| !m.is_adult.unwrap_or_default())
        .filter_map(|m| {
            m.title
                .as_ref()?
                .romaji
                .as_ref()
                .map(|t| format!("[{t}]({})", anilist_media_url!(MediaType, m.type_, m.id)))
        })
        .collect();

    if appearances.is_empty() {
        None
    } else {
        Some(appearances)
    }
}
