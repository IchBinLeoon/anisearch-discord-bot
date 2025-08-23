use poise::serenity_prelude::User;

use crate::Context;
use crate::error::Result;

/// 📘 Display detailed information about the given MyAnimeList profile.
#[poise::command(
    slash_command,
    rename = "myanimelist",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn myanimelist_slash_command(
    ctx: Context<'_>,
    #[description = "MyAnimeList username to look up."]
    #[min_length = 2]
    #[max_length = 16]
    username: Option<String>,
    #[description = "User to look up."] user: Option<User>,
) -> Result<()> {
    todo!()
}

/// 📘 Display detailed information about the given MyAnimeList profile.
#[poise::command(
    context_menu_command = "MyAnimeList Profile",
    rename = "myanimelist",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn myanimelist_context_menu_command(
    ctx: Context<'_>,
    #[description = "User to look up."] user: User,
) -> Result<()> {
    todo!()
}
