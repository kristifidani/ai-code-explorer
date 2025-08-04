use actix_web::{App, HttpServer};
use backend::{
    app_config::config_app, db::ProjectRepositoryImpl, tracing::tracing_setup,
    utils::parse_env_expect,
};
use mongodb::Client;

#[allow(clippy::expect_used)]
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenvy::dotenv().ok();
    tracing_setup();

    // get port from environment variable
    let port: u16 = parse_env_expect("APP_PORT");

    // initialize mongodb
    let mongo_uri: String = parse_env_expect("MONGO_URI");
    let mongo_db_name: String = parse_env_expect("MONGO_DB_NAME");

    let client = Client::with_uri_str(&mongo_uri)
        .await
        .expect("Failed to connect to MongoDB");
    let project_repo = ProjectRepositoryImpl::new(&client, &mongo_db_name);

    HttpServer::new(move || {
        App::new()
            .configure(config_app)
            .wrap(actix_web::middleware::Logger::default())
            .app_data(actix_web::web::Data::new(project_repo.clone()))
    })
    .bind(("127.0.0.1", port))?
    .run()
    .await
}
