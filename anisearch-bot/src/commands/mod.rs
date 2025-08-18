use poise::Command;

use crate::Data;
use crate::error::Error;

mod autocomplete;
mod choices;
mod help;
mod search;

pub fn commands() -> Vec<Command<Data, Error>> {
    vec![
        search::anime::anime(),
        search::manga::manga(),
        search::character::character(),
        search::staff::staff(),
        search::studio::studio(),
        search::trending::trending(),
        search::seasonal::seasonal(),
        search::random::random(),
        help::ping::ping(),
        help::invite::invite(),
        help::support::support(),
    ]
}
