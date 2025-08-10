#![allow(clippy::expect_used)]

use actix_web::web;
use backend::{clients::db::ProjectRepository, utils::parse_env_expect};
use mockito::{Matcher, ServerGuard};
use mongodb::Client;
use tokio::sync::OnceCell;

const TEST_DB_NAME: &str = "integration_tests_db";

// Once-per-suite initialized ProjectRepository
static PROJECT_REPO: OnceCell<web::Data<ProjectRepository>> = OnceCell::const_new();

async fn init_project_repo_once() -> web::Data<ProjectRepository> {
    // load env
    dotenvy::dotenv().ok();

    // connect to Mongo client
    let mongo_uri: String = parse_env_expect("MONGO_URI");
    let mongo_client = Client::with_uri_str(&mongo_uri)
        .await
        .expect("Failed to connect to MongoDB");

    // clean collection once per test suite
    let collection = mongo_client
        .database(TEST_DB_NAME)
        .collection::<mongodb::bson::Document>("projects");
    let _ = collection.delete_many(mongodb::bson::doc! {}).await;
    println!("[tests] Projects collection cleared");

    web::Data::new(ProjectRepository::new(&mongo_client, TEST_DB_NAME))
}

// Public helper returning a clone of the once-initialized repo
pub async fn init_db() -> web::Data<ProjectRepository> {
    PROJECT_REPO
        .get_or_init(init_project_repo_once)
        .await
        .clone()
}

// Mock AI service helpers
pub struct MockAiService;

impl MockAiService {
    #[allow(clippy::new_ret_no_self)]
    pub async fn new() -> ServerGuard {
        mockito::Server::new_async().await
    }

    pub fn create_successful_ingest_mock(
        server: &mut ServerGuard,
        expected_repo_url: &str,
    ) -> mockito::Mock {
        server
            .mock("POST", "/ingest")
            .match_header("content-type", "application/json")
            .match_body(Matcher::Json(serde_json::json!({
                "repo_url": expected_repo_url
            })))
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body("{\"status\": \"success\"}")
            .create()
    }

    #[allow(dead_code)]
    pub fn create_error_ingest_mock(
        server: &mut ServerGuard,
        expected_repo_url: &str,
        status_code: usize,
        error_message: &str,
    ) -> mockito::Mock {
        server
            .mock("POST", "/ingest")
            .match_header("content-type", "application/json")
            .match_body(Matcher::Json(serde_json::json!({
                "repo_url": expected_repo_url
            })))
            .with_status(status_code)
            .with_header("content-type", "application/json")
            .with_body(error_message)
            .create()
    }
}
