use poise::Command;

use crate::Data;
use crate::error::Error;

mod autocomplete;
mod choices;
mod help;
mod search;

pub fn commands() -> Vec<Command<Data, Error>> {
    vec![
        search::anime::anime_slash_command(),
        search::manga::manga_slash_command(),
        search::character::character_slash_command(),
        search::staff::staff_slash_command(),
        search::studio::studio_slash_command(),
        search::trending::trending_slash_command(),
        search::seasonal::seasonal_slash_command(),
        search::random::random_slash_command(),
        help::stats::stats_slash_command(),
        help::ping::ping_slash_command(),
        help::invite::invite_slash_command(),
        help::support::support_slash_command(),
    ]
}
