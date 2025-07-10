use poise::serenity_prelude::{AutocompleteChoice, CreateAutocompleteResponse};

use crate::Context;
use crate::error::Result;

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

    ctx.say(ctx.invocation_string()).await?;

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
