use anisearch_entity::users;
use poise::serenity_prelude::UserId;
use sea_orm::{DatabaseConnection, DbErr, EntityTrait, Set};
use std::sync::Arc;

pub struct UserService {
    database: Arc<DatabaseConnection>,
}

impl UserService {
    pub fn init(database: Arc<DatabaseConnection>) -> Self {
        Self { database }
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
}
