use std::sync::Arc;

use anisearch_entity::users;
use poise::serenity_prelude::UserId;
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};

use crate::on_conflict_do_update_if_changed;

pub struct UserService {
    database: Arc<DatabaseConnection>,
}

impl UserService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
    }

    pub async fn add_user(&self, id: UserId, name: String) -> Result<(), DbErr> {
        let model = users::ActiveModel {
            id: Set(id.get() as i64),
            name: Set(name),
            ..Default::default()
        };

        let on_conflict = on_conflict_do_update_if_changed!(
            users::Entity,
            users::Column::Id,
            users::Column::Name,
        );

        users::Entity::insert(model)
            .on_conflict(on_conflict)
            .do_nothing()
            .exec(self.database.as_ref())
            .await?;

        Ok(())
    }
}
