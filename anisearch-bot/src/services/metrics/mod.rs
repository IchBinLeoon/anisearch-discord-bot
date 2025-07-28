use anisearch_entity::{guild_command_usages, private_command_usages};
use poise::serenity_prelude::{GuildId, UserId};
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};
use std::sync::Arc;

pub struct MetricsService {
    database: Arc<DatabaseConnection>,
}

impl MetricsService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
    }

    pub async fn add_guild_command_usage(
        &self,
        ctx_id: u64,
        user_id: UserId,
        guild_id: GuildId,
        command_name: String,
    ) -> Result<(), DbErr> {
        let model = guild_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            user_id: Set(Some(user_id.get() as i64)),
            guild_id: Set(Some(guild_id.get() as i64)),
            command_name: Set(command_name),
            ..Default::default()
        };

        guild_command_usages::Entity::insert(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn add_private_command_usage(
        &self,
        ctx_id: u64,
        user_id: UserId,
        command_name: String,
    ) -> Result<(), DbErr> {
        let model = private_command_usages::ActiveModel {
            id: Set(ctx_id as i64),
            user_id: Set(Some(user_id.get() as i64)),
            command_name: Set(command_name),
            ..Default::default()
        };

        private_command_usages::Entity::insert(model)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }
}
