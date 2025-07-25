use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::Context;
use crate::clients::anilist::character_query::CharacterQueryPageCharacters;
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_EMOJI;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{UNKNOWN_EMBED_FIELD, format_date, format_opt, sanitize_description};

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
    let ephemeral = ephemeral.unwrap_or_default();

    if ephemeral {
        ctx.defer_ephemeral().await?;
    } else {
        ctx.defer().await?;
    }

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
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None).description(
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
        .and_then(|n| match (&n.full, &n.native) {
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
        })
        .unwrap_or(UNKNOWN_EMBED_FIELD.to_string());

    let mut embed = create_anilist_embed(title, Some("Character".to_string()));

    if let Some(desc) = &data.description {
        embed = embed.description(sanitize_description(desc, 1000));
    }

    if let Some(img) = data.image.as_ref().and_then(|i| i.large.as_ref()) {
        embed = embed.thumbnail(img);
    }

    let birthday = data.date_of_birth.as_ref();

    embed = embed
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
        .field("Gender", format_opt(data.gender.as_ref()), true);

    if let Some(name) = &data.name {
        let mut synonyms: Vec<String> = name
            .alternative
            .as_ref()
            .map(|alt| alt.iter().flatten().map(|n| format!("`{n}`")).collect())
            .unwrap_or_default();

        if let Some(spoiler) = &name.alternative_spoiler {
            synonyms.extend(spoiler.iter().flatten().map(|n| format!("||`{n}`||")));
        }

        if !synonyms.is_empty() {
            embed = embed.field("Synonyms", synonyms.join(", "), false);
        }
    }

    if let Some(media) = &data.media {
        let appearances: Vec<String> = media
            .nodes
            .as_ref()
            .map(|n| {
                n.iter()
                    .flatten()
                    .filter(|m| !m.is_adult.unwrap_or(false))
                    .filter_map(|m| m.title.as_ref()?.romaji.as_ref().map(|t| t.to_string()))
                    .collect()
            })
            .unwrap_or_default();

        if !appearances.is_empty() {
            embed = embed.field("Popular Appearances", appearances.join(" • "), false);
        }
    }

    embed
}

fn create_character_buttons(data: &CharacterQueryPageCharacters) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(format!("https://anilist.co/character/{}/", data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
}
