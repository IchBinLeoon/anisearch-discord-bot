use poise::serenity_prelude::User;

use crate::Context;
use crate::error::Result;

/// 🦊 Display detailed information about the given Kitsu profile.
#[poise::command(
    slash_command,
    rename = "kitsu",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn kitsu_slash_command(
    ctx: Context<'_>,
    #[description = "Kitsu username to look up."]
    #[min_length = 3]
    #[max_length = 20]
    username: Option<String>,
    #[description = "User to look up."] user: Option<User>,
) -> Result<()> {
    todo!()
}

/// 🦊 Display detailed information about the given Kitsu profile.
#[poise::command(
    context_menu_command = "Kitsu Profile",
    rename = "kitsu",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn kitsu_context_menu_command(
    ctx: Context<'_>,
    #[description = "User to look up."] user: User,
) -> Result<()> {
    todo!()
}
