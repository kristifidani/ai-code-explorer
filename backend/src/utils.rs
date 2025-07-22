use std::str::FromStr;

/// Tries to load the value from an environment variable and parse it into T.
///
/// # Arguments
///
/// * `key` - the environment variable key to try to load
///
/// # Panics
///
/// Panics if the environment variable does not exist or could not be parsed into T.
pub fn parse_env_expect<T: FromStr<Err = E>, E: std::fmt::Display>(key: &str) -> T {
    let value = std::env::var(key).unwrap_or_else(|_| {
        let msg = format!("Environment variable {key} not set. {key} must be set!");
        tracing::error!("{msg}");
        panic!("{msg}")
    });

    value.parse().unwrap_or_else(|e| {
        let msg = format!(
            "Failed to parse value '{value}' from {key} into '{}': {e}",
            std::any::type_name::<T>()
        );
        tracing::error!("{msg}");
        panic!("{msg}")
    })
}
