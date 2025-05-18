use migration::MigratorTrait;
use sea_orm::{ConnectOptions, Database, DatabaseConnection};
use tracing::Level;
use tracing::log::LevelFilter;

use crate::error::Result;

pub async fn create_database_connection<M>(database_uri: &str) -> Result<DatabaseConnection>
where
    M: MigratorTrait,
{
    let mut options = ConnectOptions::new(database_uri);

    if tracing::enabled!(Level::DEBUG) {
        options.sqlx_logging_level(LevelFilter::Debug);
    } else {
        options.sqlx_logging(false);
    }

    let db = Database::connect(options).await?;

    run_migrations::<M>(&db).await?;

    Ok(db)
}

async fn run_migrations<M>(db: &DatabaseConnection) -> Result<()>
where
    M: MigratorTrait,
{
    M::install(db).await?;

    M::up(db, None).await?;

    Ok(())
}
