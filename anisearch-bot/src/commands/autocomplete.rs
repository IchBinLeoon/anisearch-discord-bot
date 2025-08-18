use poise::serenity_prelude::{AutocompleteChoice, CreateAutocompleteResponse};

use crate::Context;
use crate::clients::anilist::error::AniListError;

async fn autocomplete<'a, F, Fut>(
    partial: &'a str,
    autocomplete_fn: F,
) -> CreateAutocompleteResponse<'a>
where
    F: FnOnce(String) -> Fut,
    Fut: Future<Output = Result<Vec<String>, AniListError>>,
{
    let values = autocomplete_fn(partial.trim().to_string())
        .await
        .unwrap_or_default();

    let choices: Vec<AutocompleteChoice> =
        values.into_iter().map(AutocompleteChoice::from).collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

pub async fn autocomplete_anime_title<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete(partial, |query| async {
        ctx.data().anilist_service.anime_autocomplete(query).await
    })
    .await
}

pub async fn autocomplete_manga_title<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete(partial, |query| async {
        ctx.data().anilist_service.manga_autocomplete(query).await
    })
    .await
}

pub async fn autocomplete_character_name<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete(partial, |query| async {
        ctx.data()
            .anilist_service
            .character_autocomplete(query)
            .await
    })
    .await
}

pub async fn autocomplete_staff_name<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete(partial, |query| async {
        ctx.data().anilist_service.staff_autocomplete(query).await
    })
    .await
}

pub async fn autocomplete_studio_name<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete(partial, |query| async {
        ctx.data().anilist_service.studio_autocomplete(query).await
    })
    .await
}

async fn autocomplete_comma_separated<'a, F, Fut>(
    partial: &'a str,
    autocomplete_fn: F,
) -> CreateAutocompleteResponse<'a>
where
    F: FnOnce(String) -> Fut,
    Fut: Future<Output = Result<Vec<String>, AniListError>>,
{
    let parts: Vec<&str> = partial.split(',').map(str::trim).collect();

    let (complete, incomplete) = match parts.split_last() {
        Some((last, rest)) => (rest.join(", "), last.to_string()),
        None => (String::new(), String::new()),
    };

    let values = autocomplete_fn(incomplete).await.unwrap_or_default();

    let choices: Vec<AutocompleteChoice> = values
        .into_iter()
        .map(|value| {
            let choice = if complete.is_empty() {
                value
            } else {
                format!("{complete}, {value}")
            };

            AutocompleteChoice::from(choice)
        })
        .collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}

pub async fn autocomplete_genres<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete_comma_separated(partial, |query| async {
        ctx.data().anilist_service.genres_autocomplete(query).await
    })
    .await
}

pub async fn autocomplete_tags<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    autocomplete_comma_separated(partial, |query| async {
        ctx.data().anilist_service.tags_autocomplete(query).await
    })
    .await
}
