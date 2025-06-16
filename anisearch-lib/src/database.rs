use sea_orm::{ConnectOptions, ConnectionTrait, Database, DatabaseConnection, DbErr, Statement};
use sea_orm_migration::MigratorTrait;
use tracing::Level;
use tracing::log::LevelFilter;

pub async fn create_database_connection<M>(database_uri: &str) -> Result<DatabaseConnection, DbErr>
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

async fn run_migrations<M>(db: &DatabaseConnection) -> Result<(), DbErr>
where
    M: MigratorTrait,
{
    M::install(db).await?;

    M::up(db, None).await?;

    Ok(())
}

pub async fn get_database_version(db: &DatabaseConnection) -> Result<String, DbErr> {
    let stmt = Statement::from_string(db.get_database_backend(), "SELECT version();");

    let version = db
        .query_one(stmt)
        .await?
        .and_then(|r| r.try_get("", "version").ok())
        .unwrap_or("unknown version".to_string());

    Ok(version)
}
