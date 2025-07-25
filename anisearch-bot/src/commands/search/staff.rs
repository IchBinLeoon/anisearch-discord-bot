use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::Context;
use crate::clients::anilist::staff_query::StaffQueryPageStaff;
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_EMOJI;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{UNKNOWN_EMBED_FIELD, format_date, format_opt, sanitize_description};

/// 🎬 Search for a staff and display detailed information.
#[poise::command(
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn staff(
    ctx: Context<'_>,
    #[description = "Name of the staff to search for."]
    #[autocomplete = "autocomplete_name"]
    name: String,
    #[description = "Maximum number of results to display."]
    #[min = 1]
    #[max = 15]
    limit: Option<usize>,
) -> Result<()> {
    ctx.defer().await?;

    let data = ctx.data();

    match data
        .anilist_service
        .search_staff(name.clone(), limit)
        .await?
    {
        Some(staff) => {
            let pages = staff
                .iter()
                .map(|data| {
                    Page::new(create_staff_embed(data)).add_link_buttons(create_staff_buttons(data))
                })
                .collect();

            let mut paginator = Paginator::builder().pages(pages).build();

            paginator.paginate(ctx).await?;
        }
        None => {
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None).description(
                format!("A staff with the name `{name}` could not be found."),
            );

            let reply = CreateReply::new().embed(embed);

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
        .staff_autocomplete(partial.trim().to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> =
        names.into_iter().map(AutocompleteChoice::from).collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

fn create_staff_embed(data: &StaffQueryPageStaff) -> CreateEmbed {
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

    let mut embed = create_anilist_embed(title, Some("Staff".to_string()));

    if let Some(desc) = &data.description {
        embed = embed.description(sanitize_description(desc, 1000));
    }

    if let Some(img) = data.image.as_ref().and_then(|i| i.large.as_ref()) {
        embed = embed.thumbnail(img);
    }

    let birthday = data.date_of_birth.as_ref();
    let occupations: Option<String> = data.primary_occupations.as_ref().map(|o| {
        o.iter()
            .flatten()
            .cloned()
            .collect::<Vec<String>>()
            .join(", ")
    });

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
        .field("Age", format_opt(data.age), true)
        .field("Gender", format_opt(data.gender.as_ref()), true)
        .field("Hometown", format_opt(data.home_town.as_ref()), true)
        .field("Language", format_opt(data.language_v2.as_ref()), true)
        .field("Primary Occupations", format_opt(occupations), true);

    if let Some(alt) = data.name.as_ref().and_then(|n| n.alternative.as_ref()) {
        let synonyms: Vec<String> = alt.iter().flatten().map(|n| format!("`{n}`")).collect();

        if !synonyms.is_empty() {
            embed = embed.field("Synonyms", synonyms.join(", "), false);
        }
    }

    if let Some(media) = &data.staff_media {
        let staff_roles: Vec<String> = media
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

        if !staff_roles.is_empty() {
            embed = embed.field("Popular Staff Roles", staff_roles.join(" • "), false);
        }
    }

    if let Some(characters) = &data.characters {
        let character_roles: Vec<String> = characters
            .nodes
            .as_ref()
            .map(|n| {
                n.iter()
                    .flatten()
                    .filter_map(|m| m.name.as_ref()?.full.as_ref().map(|t| t.to_string()))
                    .collect()
            })
            .unwrap_or_default();

        if !character_roles.is_empty() {
            embed = embed.field(
                "Popular Character Roles",
                character_roles.join(" • "),
                false,
            );
        }
    }

    embed
}

fn create_staff_buttons(data: &StaffQueryPageStaff) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(format!("https://anilist.co/staff/{}/", data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
}
