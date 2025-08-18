use poise::CreateReply;
use poise::serenity_prelude::{CreateActionRow, CreateComponent};

use crate::Context;
use crate::commands::autocomplete::{autocomplete_genres, autocomplete_tags};
use crate::commands::choices::MediaChoice;
use crate::commands::search::anime::{create_media_buttons, create_media_embed};
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
    #[autocomplete = autocomplete_genres]
    genres: Option<String>,
    #[description = "Comma-separated list of tags."]
    #[autocomplete = autocomplete_tags]
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
