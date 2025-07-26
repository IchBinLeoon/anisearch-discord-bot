use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateAutocompleteResponse, CreateButton, CreateEmbed,
};

use crate::Context;
use crate::clients::anilist::staff_query::StaffQueryPageStaff;
use crate::commands::search::character::format_name;
use crate::components::paginate::{Page, Paginator};
use crate::error::Result;
use crate::utils::ANILIST_EMOJI;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;
use crate::utils::format::{format_date, format_opt, sanitize_description};

/// 🎬 Search for a staff and display detailed information.
#[poise::command(
    category = "Search",
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
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

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

            let mut paginator = Paginator::builder()
                .pages(pages)
                .ephemeral(ephemeral)
                .build();

            paginator.paginate(ctx).await?;
        }
        None => {
            let embed = create_anilist_embed("🚫 Not Found".to_string(), None).description(
                format!("A staff with the name `{name}` could not be found."),
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
        .and_then(|n| format_name(n.full.as_ref(), n.native.as_ref()));

    let mut embed = create_anilist_embed(format_opt(title), Some("Staff".to_string()));

    if let Some(desc) = &data.description {
        embed = embed.description(sanitize_description(desc, 1000));
    }

    if let Some(img) = data.image.as_ref().and_then(|i| i.large.as_ref()) {
        embed = embed.thumbnail(img);
    }

    embed = add_basic_fields(embed, data);
    embed = add_synonyms(embed, data);
    embed = add_staff_roles(embed, data);
    embed = add_character_roles(embed, data);

    embed
}

fn create_staff_buttons(data: &StaffQueryPageStaff) -> Vec<CreateButton> {
    vec![
        CreateButton::new_link(format!("https://anilist.co/staff/{}/", data.id))
            .label("AniList")
            .emoji(ANILIST_EMOJI),
    ]
}

fn add_basic_fields<'a>(embed: CreateEmbed<'a>, data: &StaffQueryPageStaff) -> CreateEmbed<'a> {
    let birthday = data.date_of_birth.as_ref();

    let occupations: Option<String> = data.primary_occupations.as_ref().map(|o| {
        o.iter()
            .flatten()
            .cloned()
            .collect::<Vec<String>>()
            .join(", ")
    });

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
        .field("Hometown", format_opt(data.home_town.as_ref()), true)
        .field("Language", format_opt(data.language_v2.as_ref()), true)
        .field("Primary Occupations", format_opt(occupations), true)
}

fn add_synonyms<'a>(mut embed: CreateEmbed<'a>, data: &StaffQueryPageStaff) -> CreateEmbed<'a> {
    if let Some(synonyms) = extract_synonyms(data) {
        embed = embed.field("Synonyms", synonyms.join(", "), false);
    }

    embed
}

fn extract_synonyms(data: &StaffQueryPageStaff) -> Option<Vec<String>> {
    let name = data.name.as_ref()?;
    let alt = name.alternative.as_ref()?;

    let synonyms: Vec<String> = alt.iter().flatten().map(|n| format!("`{n}`")).collect();

    if synonyms.is_empty() {
        None
    } else {
        Some(synonyms)
    }
}

fn add_staff_roles<'a>(mut embed: CreateEmbed<'a>, data: &StaffQueryPageStaff) -> CreateEmbed<'a> {
    if let Some(staff_roles) = extract_staff_roles(data) {
        embed = embed.field("Popular Staff Roles", staff_roles.join(" • "), false);
    }

    embed
}

fn extract_staff_roles(data: &StaffQueryPageStaff) -> Option<Vec<String>> {
    let media = data.staff_media.as_ref()?;
    let nodes = media.nodes.as_ref()?;

    let staff_roles: Vec<String> = nodes
        .iter()
        .flatten()
        .filter(|m| !m.is_adult.unwrap_or_default())
        .filter_map(|m| m.title.as_ref()?.romaji.as_ref().map(|t| t.to_string()))
        .collect();

    if staff_roles.is_empty() {
        None
    } else {
        Some(staff_roles)
    }
}

fn add_character_roles<'a>(
    mut embed: CreateEmbed<'a>,
    data: &StaffQueryPageStaff,
) -> CreateEmbed<'a> {
    if let Some(character_roles) = extract_character_roles(data) {
        embed = embed.field(
            "Popular Character Roles",
            character_roles.join(" • "),
            false,
        );
    }

    embed
}

fn extract_character_roles(data: &StaffQueryPageStaff) -> Option<Vec<String>> {
    let characters = data.characters.as_ref()?;
    let nodes = characters.nodes.as_ref()?;

    let character_roles: Vec<String> = nodes
        .iter()
        .flatten()
        .filter_map(|m| m.name.as_ref()?.full.as_ref().map(|t| t.to_string()))
        .collect();

    if character_roles.is_empty() {
        None
    } else {
        Some(character_roles)
    }
}
