pub mod anilist;
pub mod guild;
pub mod metrics;
pub mod user;

#[macro_export]
macro_rules! on_conflict_do_update_if_changed {
    ($entity:expr, $pkey:expr, $($column:expr),+ $(,)?) => {
        sea_orm::sea_query::OnConflict::column($pkey)
            .update_columns([$($column),+])
            .action_cond_where(
                sea_orm::Condition::any()
                $(
                    .add(
                        sea_orm::sea_query::Expr::col(($entity, $column)).ne(
                            sea_orm::sea_query::Expr::cust_with_expr(
                                r#""excluded".$1"#,
                                sea_orm::sea_query::Expr::col($column),
                            )
                        )
                    )
                )+
            )
            .to_owned()
    };
}
