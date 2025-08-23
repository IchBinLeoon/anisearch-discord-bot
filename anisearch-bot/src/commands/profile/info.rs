use poise::serenity_prelude::User;

use crate::Context;
use crate::error::Result;

/// 👤 View the added profiles of a user.
#[poise::command(
    slash_command,
    rename = "info",
    category = "Profile",
    install_context = "Guild|User",
    interaction_context = "Guild|BotDm|PrivateChannel"
)]
pub async fn profile_info_slash_command(
    ctx: Context<'_>,
    #[description = "User to look up."] user: Option<User>,
) -> Result<()> {
    todo!()
}
