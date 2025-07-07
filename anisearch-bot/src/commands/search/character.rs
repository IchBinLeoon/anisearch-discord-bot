use poise::serenity_prelude::{AutocompleteChoice, CreateAutocompleteResponse};

use crate::Context;
use crate::error::Result;

/// 🎭 Search for a character and display detailed information.
#[poise::command(
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
    limit: Option<u8>,
) -> Result<()> {
    ctx.defer().await?;

    ctx.say(ctx.invocation_string()).await?;

    Ok(())
}

async fn autocomplete_name<'a>(
    ctx: Context<'a>,
    partial: &'a str,
) -> CreateAutocompleteResponse<'a> {
    let choices: Vec<_> = ["Choice One", "Choice Two", "Choice Three"]
        .into_iter()
        .filter(move |name| name.to_lowercase().starts_with(&partial.to_lowercase()))
        .map(AutocompleteChoice::from)
        .collect();

    CreateAutocompleteResponse::new().set_choices(choices)
}
