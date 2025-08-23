use poise::serenity_prelude::User;

use crate::Context;
use crate::error::Result;

/// 💠 Display detailed information about the given AniList profile.
#[poise::command(
    slash_command,
    rename = "anilist",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn anilist_slash_command(
    ctx: Context<'_>,
    #[description = "AniList username to look up."]
    #[min_length = 2]
    #[max_length = 20]
    username: Option<String>,
    #[description = "User to look up."] user: Option<User>,
) -> Result<()> {
    todo!()
}

/// 💠 Display detailed information about the given AniList profile.
#[poise::command(
    context_menu_command = "AniList Profile",
    rename = "anilist",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn anilist_context_menu_command(
    ctx: Context<'_>,
    #[description = "User to look up."] user: User,
) -> Result<()> {
    todo!()
}
