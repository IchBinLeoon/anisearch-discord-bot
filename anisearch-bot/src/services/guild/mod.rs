use std::sync::Arc;

use anisearch_entity::guilds;
use poise::serenity_prelude::GuildId;
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};

use crate::on_conflict_do_update_if_changed;

pub struct GuildService {
    database: Arc<DatabaseConnection>,
}

impl GuildService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
    }

    pub async fn add_guild(&self, id: GuildId, name: String) -> Result<(), DbErr> {
        let model = guilds::ActiveModel {
            id: Set(id.get() as i64),
            name: Set(name),
            ..Default::default()
        };

        let on_conflict = on_conflict_do_update_if_changed!(
            guilds::Entity,
            guilds::Column::Id,
            guilds::Column::Name,
        );

        guilds::Entity::insert(model)
            .on_conflict(on_conflict)
            .do_nothing()
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }

    pub async fn remove_guild(&self, id: GuildId) -> Result<(), DbErr> {
        guilds::Entity::delete_by_id(id.get() as i64)
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }
}
