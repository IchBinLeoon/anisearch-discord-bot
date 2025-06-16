use anisearch_lib::config;

config!(
    address("ADDRESS"): String = "0.0.0.0:8080".to_string(),
    database_uri("DATABASE_URI"): String,
    grpc_uri("GRPC_URI"): String,
);
