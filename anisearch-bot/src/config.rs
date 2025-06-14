use anisearch_lib::config;
use poise::serenity_prelude::{GuildId, Token};

config!(
    token("TOKEN"): Token,
    database_uri("DATABASE_URI"): String,
    testing_guild("TESTING_GUILD"): Option<GuildId>,
    total_shards("TOTAL_SHARDS"): Option<u16>,
);
