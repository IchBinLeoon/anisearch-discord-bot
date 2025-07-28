use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
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
        manager
            .drop_table(Table::drop().table(Guilds::Table).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(Users::Table).to_owned())
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
enum GuildCommandUsages {
    Table,
    Id,
    UserId,
    GuildId,
    CommandName,
    UsedAt,
}

#[derive(DeriveIden)]
enum PrivateCommandUsages {
    Table,
    Id,
    UserId,
    CommandName,
    UsedAt,
}
