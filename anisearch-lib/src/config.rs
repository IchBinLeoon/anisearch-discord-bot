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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_value() {
        config! {
            test("TEST"): u32,
        }

        unsafe {
            std::env::set_var("TEST", "42");
        }

        assert_eq!(Config::init().unwrap().test, 42);
    }

    #[test]
    fn test_value_default() {
        config! {
            test("TEST_DEFAULT"): u32 = 42,
        }

        assert_eq!(Config::init().unwrap().test, 42);

        unsafe {
            std::env::set_var("TEST_DEFAULT", "69");
        }

        assert_eq!(Config::init().unwrap().test, 69);
    }

    #[test]
    fn test_value_optional() {
        config! {
            test("TEST_OPTIONAL"): Option<u32>,
        }

        assert_eq!(Config::init().unwrap().test, None);

        unsafe {
            std::env::set_var("TEST_OPTIONAL", "42");
        }

        assert_eq!(Config::init().unwrap().test, Some(42));
    }

    #[test]
    fn test_value_missing() {
        config! {
            _test("TEST_MISSING"): u32,
        }

        assert!(Config::init().is_err());
    }
}
