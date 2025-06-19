use poise::Command;

use crate::Data;
use crate::error::Error;

mod help;

pub fn commands() -> Vec<Command<Data, Error>> {
    vec![
        help::ping::ping(),
        help::invite::invite(),
        help::support::support(),
    ]
}
