use poise::CreateReply;
use poise::serenity_prelude::{
    AutocompleteChoice, CreateActionRow, CreateAutocompleteResponse, CreateComponent,
};

use crate::Context;
use crate::clients::anilist::error::AniListError;
use crate::clients::anilist::media_query::MediaType;
use crate::commands::search::anime::{create_media_buttons, create_media_embed};
use crate::commands::search::trending::MediaChoice;
use crate::error::Result;
use crate::utils::commands::defer_with_ephemeral;
use crate::utils::embeds::create_anilist_embed;

/// 🎲 Display a random anime or manga.
#[poise::command(
    category = "Search",
    slash_command,
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn random(
    ctx: Context<'_>,
    #[description = "Type of media."] media: Option<MediaChoice>,
    #[description = "Comma-separated list of genres."]
    #[autocomplete = "autocomplete_genres"]
    genres: Option<String>,
    #[description = "Comma-separated list of tags."]
    #[autocomplete = "autocomplete_tags"]
    tags: Option<String>,
    #[description = "Show results only to you."] ephemeral: Option<bool>,
) -> Result<()> {
    let ephemeral = defer_with_ephemeral(ctx, ephemeral).await?;

    let data = ctx.data();

    let media = data
        .anilist_service
        .random(
            media.map(|m| m.into()),
            genres.map(|g| g.split(',').map(|s| s.trim().to_string()).collect()),
            tags.map(|t| t.split(',').map(|s| s.trim().to_string()).collect()),
        )
        .await?;

    let (embed, buttons) = match media {
        Some(ref media) => {
            let embed = create_media_embed(media);
            let buttons = Some(create_media_buttons(media));

            (embed, buttons)
        }
        None => (
            create_anilist_embed("🚫 Not Found".to_string(), None, None)
                .description("Random media could not be found."),
            None,
        ),
    };

    let components = if let Some(ref buttons) = buttons {
        vec![CreateComponent::ActionRow(CreateActionRow::buttons(
            buttons,
        ))]
    } else {
        vec![]
    };

    let reply = CreateReply::new()
        .embed(embed)
        .components(components)
        .ephemeral(ephemeral);

    ctx.send(reply).await?;

    Ok(())
}

async fn autocomplete_genres<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete_comma_separated(partial, |tag| async {
        let data = ctx.data();

        data.anilist_service.genres_autocomplete(tag).await
    })
    .await
}

async fn autocomplete_tags<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete_comma_separated(partial, |genre| async {
        let data = ctx.data();

        data.anilist_service.tags_autocomplete(genre).await
    })
    .await
}

async fn autocomplete_comma_separated<'a, F, Fut>(
    partial: &'a str,
    autocomplete: F,
) -> CreateAutocompleteResponse<'a>
where
    F: FnOnce(String) -> Fut,
    Fut: Future<Output = Result<Vec<String>, AniListError>>,
{
    let mut parts: Vec<&str> = partial.split(',').map(str::trim).collect();
    let incomplete = parts.pop().unwrap_or_default();

    let results: Vec<String> = autocomplete(incomplete.to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> = results
        .into_iter()
        .map(|r| {
            let mut full = parts.clone();
            full.push(&r);

            AutocompleteChoice::from(full.join(", "))
        })
        .collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

impl From<MediaChoice> for MediaType {
    fn from(value: MediaChoice) -> Self {
        match value {
            MediaChoice::Anime => MediaType::ANIME,
            MediaChoice::Manga => MediaType::MANGA,
        }
    }
}
