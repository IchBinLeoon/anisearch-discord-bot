use anisearch_entity::{guild_command_usages, private_command_usages, users};
use poise::serenity_prelude::{GuildId, UserId};
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};
use std::sync::Arc;

use crate::services::guild::GuildService;

pub struct UserService {
    database: Arc<DatabaseConnection>,
    guild_service: Arc<GuildService>,
}

impl UserService {
    pub fn init(database: Arc<DatabaseConnection>, guild_service: Arc<GuildService>) -> Self {
        Self {
            database,
            guild_service,
        }
    }

    pub async fn add_user(&self, user_id: UserId) -> Result<(), DbErr> {
        let model = users::ActiveModel {
            id: Set(user_id.get() as i64),
            ..Default::default()
        };

        users::Entity::insert(model)
            .on_conflict_do_nothing()
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn add_guild_command_usage(
        &self,
        ctx_id: u64,
        user_id: UserId,
        guild_id: GuildId,
        command_name: String,
    ) -> Result<(), DbErr> {
        self.add_user(user_id).await?;
        self.guild_service.add_guild(guild_id).await?;

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
        self.add_user(user_id).await?;

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
