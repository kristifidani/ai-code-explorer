use actix_cors::Cors;
use actix_web::{App, HttpServer};
use backend::{
    app_config::config_app, clients::db::ProjectRepository, tracing::tracing_setup,
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

    // Initialize mongodb
    let mongo_uri: String = parse_env_expect("MONGO_URI");
    let mongo_db_name: String = parse_env_expect("MONGO_DB_NAME");
    let client = Client::with_uri_str(&mongo_uri)
        .await
        .expect("Failed to connect to MongoDB");
    let project_repo = actix_web::web::Data::new(ProjectRepository::new(&client, &mongo_db_name));

    // Initialize AiServiceClient
    let ai_service_url: url::Url = parse_env_expect("AI_SERVICE_URL");
    let ai_service_client = actix_web::web::Data::new(
        backend::clients::ai_service_client::AiServiceClient::new(ai_service_url),
    );

    HttpServer::new(move || {
        // Configure CORS for development
        // TODO: In production, replace with specific frontend domain
        let cors = Cors::default()
            .allowed_origin("http://localhost:5173") // Vite dev server default port
            // .allowed_origin("http://localhost:5174") // Vite dev server backup port
            .allowed_methods(vec!["GET", "POST"]) // Only methods we actually use
            .allowed_headers(vec!["Content-Type", "Accept"])
            .max_age(3600);

        App::new()
            .configure(config_app)
            .wrap(cors)
            .wrap(actix_web::middleware::Logger::default())
            .app_data(project_repo.clone())
            .app_data(ai_service_client.clone())
    })
    .bind(("127.0.0.1", port))?
    .run()
    .await
}
