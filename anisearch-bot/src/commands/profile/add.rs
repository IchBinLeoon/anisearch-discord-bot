use crate::Context;
use crate::commands::choices::TrackingSiteChoice;
use crate::error::Result;

/// ➕ Add an AniList, MyAnimeList or Kitsu profile to your account.
#[poise::command(
    slash_command,
    rename = "add",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn profile_add_slash_command(
    ctx: Context<'_>,
    #[description = "Anime tracking site."] site: TrackingSiteChoice,
    #[description = "Username on the site."]
    #[min_length = 2]
    #[max_length = 20]
    username: String,
) -> Result<()> {
    todo!()
}
