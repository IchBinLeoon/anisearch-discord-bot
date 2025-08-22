use poise::serenity_prelude::{EmojiId, UserId};

pub mod commands;
pub mod embeds;
pub mod format;
pub mod urls;

pub const ANILIST_LOGO: &str =
    "https://cdn.discordapp.com/attachments/978016869342658630/978033399107289189/anilist.png";

pub const ANILIST_EMOJI: EmojiId = EmojiId::new(1391599698099572847);
pub const MYANIMELIST_EMOJI: EmojiId = EmojiId::new(1391599739845480468);

pub const ANILIST_BASE_URL: &str = "https://anilist.co";
pub const MYANIMELIST_BASE_URL: &str = "https://myanimelist.net";

pub const CREATOR: UserId = UserId::new(223871059068321793);
