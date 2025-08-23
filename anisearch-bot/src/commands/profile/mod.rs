use crate::Context;
use crate::commands::profile::add::profile_add_slash_command;
use crate::commands::profile::info::profile_info_slash_command;
use crate::commands::profile::remove::profile_remove_slash_command;
use crate::error::Result;

mod add;
pub mod anilist;
mod info;
pub mod kitsu;
pub mod myanimelist;
mod remove;

#[poise::command(
    slash_command,
    rename = "profile",
    category = "Profile",
    subcommands(
        "profile_add_slash_command",
        "profile_remove_slash_command",
        "profile_info_slash_command"
    )
)]
pub async fn profile_slash_command(_: Context<'_>) -> Result<()> {
    Ok(())
}
