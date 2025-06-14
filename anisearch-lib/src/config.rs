use anyhow::{Result, anyhow};
use envy::{Error, keep_names};
use serde::de::DeserializeOwned;

pub use serde_inline_default::serde_inline_default as __serde_inline_default;

pub trait ConfigTrait: DeserializeOwned {
    fn init() -> Result<Self> {
        keep_names().from_env().map_err(|e| match e {
            Error::MissingValue(value) => {
                anyhow!("Environment variable `{value}` not set")
            }
            Error::Custom(msg) => {
                anyhow!("Failed to parse environment variable: {msg}")
            }
        })
    }
}

#[macro_export]
macro_rules! config {
    (
        $( $field:ident($env:literal): $value:ty $(= $default:expr)?, )*
    ) => {
        #[$crate::config::__serde_inline_default]
        #[derive(serde::Deserialize)]
        pub struct Config {
            $(
                $(
                    #[serde_inline_default($default)]
                )?
                #[serde(rename = $env)]
                pub $field: $value,
            )*
        }

        impl $crate::config::ConfigTrait for Config {}
    };
}
