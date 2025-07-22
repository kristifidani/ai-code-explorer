use tracing_subscriber::EnvFilter;

/// Initializes the global tracing subscriber for application-wide logging.
///
/// Sets up a `tracing_subscriber` with formatted output and an environment filter that reads the `RUST_LOG` environment variable to control log levels and filtering. If the subscriber is already initialized, logs a warning instead of panicking.
///
/// # Examples
///
/// ```
/// tracing_setup();
/// tracing::info!("Application started");
/// ```
pub fn tracing_setup() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env()) // reads RUST_LOG
        .with_target(true)
        .try_init()
        .unwrap_or_else(|_| tracing::warn!("Tracing subscriber already initialized"));
}
