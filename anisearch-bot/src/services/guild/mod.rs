use anisearch_entity::guilds;
use poise::serenity_prelude::GuildId;
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};
use std::sync::Arc;

pub struct GuildService {
    database: Arc<DatabaseConnection>,
}

impl GuildService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
    }

    pub async fn add_guild(&self, guild_id: GuildId) -> Result<(), DbErr> {
        let model = guilds::ActiveModel {
            id: Set(guild_id.get() as i64),
            ..Default::default()
        };

        guilds::Entity::insert(model)
            .on_conflict_do_nothing()
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn remove_guild(&self, guild_id: GuildId) -> Result<(), DbErr> {
        guilds::Entity::delete_by_id(guild_id.get() as i64)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }
}
