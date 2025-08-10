mod utils;

use actix_web::{App, test, web};
use backend::{
    app_config::config_app,
    clients::{ai_service_client::AiServiceClient, db::ProjectRepositoryImpl},
    types::response::ApiResponse,
};
use utils::{MockAiService, init_db};

#[actix_web::test]
async fn test_health_check() {
    // Health check doesn't need dependencies
    let app = test::init_service(App::new().configure(config_app)).await;

    let req = test::TestRequest::get().uri("/health").to_request();
    let response = test::call_service(&app, req).await;

    assert_eq!(response.status(), actix_web::http::StatusCode::OK);

    let msg: ApiResponse<()> = test::read_body_json(response).await;

    assert_eq!(msg.code, 200);
    assert_eq!(msg.message, "API is healthy ✅");
    assert!(msg.data.is_none());
}

#[actix_web::test]
async fn test_ingest_project_success() {
    let project_repo = init_db().await;

    // Mock external AI service
    let expected_repo_url = "https://github.com/testowner/testrepo.git";
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_successful_ingest_mock(&mut mock_server, expected_repo_url);

    // App with dependencies
    let ai_service_client = web::Data::new(AiServiceClient::new(&mock_server.url()));
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Request
    let payload = serde_json::json!({
        "github_url": "https://github.com/TestOwner/TestRepo"
    });

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&payload)
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), actix_web::http::StatusCode::CREATED);

    let msg: ApiResponse<()> = test::read_body_json(response).await;

    assert_eq!(msg.code, 201);
    assert_eq!(msg.message, "Project ingested successfully");
    assert!(msg.data.is_none());

    // Verify mock and DB
    mock.assert();

    let stored_project = project_repo
        .as_ref()
        .find_by_github_url(expected_repo_url)
        .await
        .expect("Failed to query database")
        .expect("Project should be stored in database");

    assert_eq!(stored_project.github_url, expected_repo_url);
}
