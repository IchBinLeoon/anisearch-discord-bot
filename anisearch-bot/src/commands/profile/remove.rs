use crate::Context;
use crate::commands::choices::TrackingSiteChoice;
use crate::error::Result;

/// ❌ Remove an added AniList, MyAnimeList or Kitsu profile from your account.
#[poise::command(
    slash_command,
    rename = "remove",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn profile_remove_slash_command(
    ctx: Context<'_>,
    #[description = "Anime tracking site."] site: TrackingSiteChoice,
) -> Result<()> {
    todo!()
}
