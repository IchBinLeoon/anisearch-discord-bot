use std::env::var;
use std::fmt::Display;
use std::str::FromStr;

use anyhow::{Result, anyhow};
use poise::serenity_prelude::{GuildId, Token};

pub struct Config {
    pub token: Token,
    pub database_uri: String,
    pub testing_guild: Option<GuildId>,
    pub total_shards: Option<u16>,
}

impl Config {
    pub fn init() -> Result<Self> {
        Ok(Self {
            token: parse_env_var("TOKEN")?,
            database_uri: parse_env_var("DATABASE_URI")?,
            testing_guild: parse_env_var_opt("TESTING_GUILD")?,
            total_shards: parse_env_var_opt("TOTAL_SHARDS")?,
        })
    }
}

fn parse_env_var<T>(key: &str) -> Result<T>
where
    T: FromStr,
    <T as FromStr>::Err: Display,
{
    var(key)
        .map_err(|e| anyhow!("Environment variable `{key}` not set: {e}"))?
        .parse::<T>()
        .map_err(|e| anyhow!("Failed to parse `{key}` environment variable: {e}"))
}

fn parse_env_var_opt<T>(key: &str) -> Result<Option<T>>
where
    T: FromStr,
    <T as FromStr>::Err: Display,
{
    var(key)
        .ok()
        .map(|s| {
            s.parse::<T>()
                .map_err(|e| anyhow!("Failed to parse optional `{key}` environment variable: {e}"))
        })
        .transpose()
}
