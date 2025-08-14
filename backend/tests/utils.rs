#![allow(clippy::expect_used)]

use actix_web::web;
use backend::{clients::db::ProjectRepository, utils::parse_env_expect};
use mockito::{Matcher, ServerGuard};
use mongodb::Client;
use std::sync::OnceLock;
use tokio::sync::Mutex;

const TEST_DB_NAME: &str = "integration_tests_db";

// Global async mutex to ensure only one test accesses the database at a time
static DB_MUTEX: OnceLock<Mutex<()>> = OnceLock::new();

pub async fn init_db() -> web::Data<ProjectRepository> {
    // Get or initialize the mutex
    let mutex = DB_MUTEX.get_or_init(|| Mutex::new(()));

    // Acquire the lock to ensure sequential database access
    let _guard = mutex.lock().await;

    // load env
    dotenvy::dotenv().ok();

    // connect to Mongo client
    let mongo_uri: String = parse_env_expect("MONGO_URI");
    let mongo_client = Client::with_uri_str(&mongo_uri)
        .await
        .expect("Failed to connect to MongoDB");

    // clean collection
    let collection = mongo_client
        .database(TEST_DB_NAME)
        .collection::<mongodb::bson::Document>("projects");
    let _ = collection.delete_many(mongodb::bson::doc! {}).await;

    web::Data::new(ProjectRepository::new(&mongo_client, TEST_DB_NAME))
}

// Mock AI service helpers
pub struct MockAiService;

impl MockAiService {
    #[allow(clippy::new_ret_no_self)]
    pub async fn new() -> ServerGuard {
        mockito::Server::new_async().await
    }

    #[allow(dead_code)]
    pub fn create_successful_ingest_mock(
        server: &mut ServerGuard,
        expected_repo_url: &str,
    ) -> mockito::Mock {
        server
            .mock("POST", "/ingest")
            .match_header("content-type", "application/json")
            .match_body(Matcher::Json(serde_json::json!({
                "canonical_github_url": expected_repo_url
            })))
            .with_status(201)
            .with_header("content-type", "application/json")
            .with_body(format!(
                r#"{{"canonical_github_url": "{}"}}"#,
                expected_repo_url
            ))
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
                "canonical_github_url": expected_repo_url
            })))
            .with_status(status_code)
            .with_header("content-type", "application/json")
            .with_body(error_message)
            .create()
    }

    #[allow(dead_code)]
    pub fn create_successful_answer_mock(
        server: &mut ServerGuard,
        expected_repo_url: &str,
        expected_question: &str,
        answer_response: &str,
    ) -> mockito::Mock {
        server
            .mock("POST", "/answer")
            .match_header("content-type", "application/json")
            .match_body(Matcher::Json(serde_json::json!({
                "canonical_github_url": expected_repo_url,
                "user_question": expected_question
            })))
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(format!(r#"{{"answer": "{}"}}"#, answer_response))
            .create()
    }

    #[allow(dead_code)]
    pub fn create_error_answer_mock(
        server: &mut ServerGuard,
        expected_repo_url: &str,
        expected_question: &str,
        status_code: usize,
        error_message: &str,
    ) -> mockito::Mock {
        server
            .mock("POST", "/answer")
            .match_header("content-type", "application/json")
            .match_body(Matcher::Json(serde_json::json!({
                "canonical_github_url": expected_repo_url,
                "user_question": expected_question
            })))
            .with_status(status_code)
            .with_header("content-type", "application/json")
            .with_body(error_message)
            .create()
    }
}
