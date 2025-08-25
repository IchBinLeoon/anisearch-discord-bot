use sea_orm::{EnumIter, Iterable};
use sea_orm_migration::prelude::extension::postgres::Type;
use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();

        db.execute_unprepared(
            "
                CREATE FUNCTION update_modified_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.modified_at = now();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            ",
        )
        .await?;

        manager
            .create_table(
                Table::create()
                    .table(Guilds::Table)
                    .col(
                        ColumnDef::new(Guilds::Id)
                            .big_integer()
                            .not_null()
                            .primary_key(),
                    )
                    .col(
                        ColumnDef::new(Guilds::AddedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(Users::Table)
                    .col(
                        ColumnDef::new(Users::Id)
                            .big_integer()
                            .not_null()
                            .primary_key(),
                    )
                    .col(
                        ColumnDef::new(Users::AddedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_type(
                Type::create()
                    .as_enum(TrackingSite)
                    .values(TrackingSiteVariants::iter())
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(UserProfiles::Table)
                    .col(
                        ColumnDef::new(UserProfiles::UserId)
                            .big_integer()
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(UserProfiles::TrackingSite)
                            .enumeration(TrackingSite, TrackingSiteVariants::iter())
                            .not_null(),
                    )
                    .col(ColumnDef::new(UserProfiles::ProfileId).integer().not_null())
                    .col(ColumnDef::new(UserProfiles::ProfileName).text().not_null())
                    .col(
                        ColumnDef::new(UserProfiles::AddedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .col(
                        ColumnDef::new(UserProfiles::ModifiedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .primary_key(
                        Index::create()
                            .col(UserProfiles::UserId)
                            .col(UserProfiles::TrackingSite)
                            .primary(),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .from_tbl(UserProfiles::Table)
                            .from_col(UserProfiles::UserId)
                            .to_tbl(Users::Table)
                            .to_col(Users::Id)
                            .on_delete(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        db.execute_unprepared(
            "
                CREATE TRIGGER user_profiles_update_modified_at_trigger
                BEFORE UPDATE ON user_profiles
                FOR EACH ROW
                EXECUTE FUNCTION update_modified_at();
            ",
        )
        .await?;

        manager
            .create_type(
                Type::create()
                    .as_enum(CommandType)
                    .values(CommandTypeVariants::iter())
                    .to_owned(),
            )
            .await?;

        manager
            .create_type(
                Type::create()
                    .as_enum(ExecutionStatus)
                    .values(ExecutionStatusVariants::iter())
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(GuildCommandUsages::Table)
                    .col(
                        ColumnDef::new(GuildCommandUsages::Id)
                            .big_integer()
                            .not_null()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(GuildCommandUsages::UserId).big_integer())
                    .col(ColumnDef::new(GuildCommandUsages::GuildId).big_integer())
                    .col(
                        ColumnDef::new(GuildCommandUsages::CommandName)
                            .text()
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(GuildCommandUsages::CommandType)
                            .enumeration(CommandType, CommandTypeVariants::iter())
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(GuildCommandUsages::ExecutionStatus)
                            .enumeration(ExecutionStatus, ExecutionStatusVariants::iter())
                            .not_null(),
                    )
                    .col(ColumnDef::new(GuildCommandUsages::ExecutionTime).integer())
                    .col(
                        ColumnDef::new(GuildCommandUsages::UsedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .from_tbl(GuildCommandUsages::Table)
                            .from_col(GuildCommandUsages::UserId)
                            .to_tbl(Users::Table)
                            .to_col(Users::Id)
                            .on_delete(ForeignKeyAction::SetNull),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .from_tbl(GuildCommandUsages::Table)
                            .from_col(GuildCommandUsages::GuildId)
                            .to_tbl(Guilds::Table)
                            .to_col(Guilds::Id)
                            .on_delete(ForeignKeyAction::SetNull),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(PrivateCommandUsages::Table)
                    .col(
                        ColumnDef::new(PrivateCommandUsages::Id)
                            .big_integer()
                            .not_null()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(PrivateCommandUsages::UserId).big_integer())
                    .col(
                        ColumnDef::new(PrivateCommandUsages::CommandName)
                            .text()
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(PrivateCommandUsages::CommandType)
                            .enumeration(CommandType, CommandTypeVariants::iter())
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(PrivateCommandUsages::ExecutionStatus)
                            .enumeration(ExecutionStatus, ExecutionStatusVariants::iter())
                            .not_null(),
                    )
                    .col(ColumnDef::new(PrivateCommandUsages::ExecutionTime).integer())
                    .col(
                        ColumnDef::new(PrivateCommandUsages::UsedAt)
                            .timestamp()
                            .not_null()
                            .default(Keyword::CurrentTimestamp),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .from_tbl(PrivateCommandUsages::Table)
                            .from_col(PrivateCommandUsages::UserId)
                            .to_tbl(Users::Table)
                            .to_col(Users::Id)
                            .on_delete(ForeignKeyAction::SetNull),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();

        db.execute_unprepared("DROP FUNCTION update_modified_at();")
            .await?;

        manager
            .drop_table(Table::drop().table(Guilds::Table).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(Users::Table).to_owned())
            .await?;

        manager
            .drop_type(Type::drop().name(TrackingSite).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(UserProfiles::Table).to_owned())
            .await?;

        db.execute_unprepared(
            "
                DROP TRIGGER user_profiles_update_modified_at_trigger
                ON user_profiles;
            ",
        )
        .await?;

        manager
            .drop_type(Type::drop().name(CommandType).to_owned())
            .await?;

        manager
            .drop_type(Type::drop().name(ExecutionStatus).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(GuildCommandUsages::Table).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(PrivateCommandUsages::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum Guilds {
    Table,
    Id,
    AddedAt,
}

#[derive(Iden)]
enum Users {
    Table,
    Id,
    AddedAt,
}

#[derive(DeriveIden)]
struct TrackingSite;

#[derive(DeriveIden, EnumIter)]
enum TrackingSiteVariants {
    #[sea_orm(iden = "anilist")]
    AniList,
    #[sea_orm(iden = "myanimelist")]
    MyAnimeList,
    #[sea_orm(iden = "kitsu")]
    Kitsu,
}

#[derive(DeriveIden)]
enum UserProfiles {
    Table,
    UserId,
    TrackingSite,
    ProfileId,
    ProfileName,
    AddedAt,
    ModifiedAt,
}

#[derive(DeriveIden)]
struct CommandType;

#[derive(DeriveIden, EnumIter)]
enum CommandTypeVariants {
    ChatInput,
    User,
    Message,
}

#[derive(DeriveIden)]
struct ExecutionStatus;

#[derive(DeriveIden, EnumIter)]
enum ExecutionStatusVariants {
    Running,
    Success,
    Error,
}

#[derive(DeriveIden)]
enum GuildCommandUsages {
    Table,
    Id,
    UserId,
    GuildId,
    CommandName,
    CommandType,
    ExecutionStatus,
    ExecutionTime,
    UsedAt,
}

#[derive(DeriveIden)]
enum PrivateCommandUsages {
    Table,
    Id,
    UserId,
    CommandName,
    CommandType,
    ExecutionStatus,
    ExecutionTime,
    UsedAt,
}
