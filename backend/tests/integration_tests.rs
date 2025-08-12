mod utils;

use actix_web::{App, http::StatusCode, test, web};
use backend::{
    app_config::config_app,
    clients::{ai_service_client::AiServiceClient, db::ProjectRepositoryImpl},
    types::{entities::ProjectEntity, response::ApiResponse},
};
use rstest::rstest;
use utils::{MockAiService, init_db};

#[actix_web::test]
async fn test_health_check() {
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

    // Test basic successful ingestion flow
    let input_url = "https://github.com/TestOwner/TestRepo";
    let expected_canonical = "https://github.com/testowner/testrepo.git";

    // Mock AI service
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_successful_ingest_mock(&mut mock_server, expected_canonical);

    let ai_service_client = web::Data::new(AiServiceClient::new(&mock_server.url()));
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(serde_json::json!({ "github_url": input_url }))
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), actix_web::http::StatusCode::CREATED);

    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 201);
    assert_eq!(msg.message, "Project ingested successfully");
    assert!(msg.data.is_none());

    mock.assert();

    let stored_project = project_repo
        .as_ref()
        .find_by_github_url(expected_canonical)
        .await
        .expect("DB query failed")
        .expect("Project should exist in DB");
    assert_eq!(stored_project.github_url, expected_canonical);
}

#[actix_web::test]
async fn test_ingest_project_already_exists() {
    let project_repo = init_db().await;

    // Pre-insert project with canonical form
    let github_url = "https://github.com/Already/Exists";
    let preexisting = ProjectEntity::new_validated(github_url).expect("valid canonical");
    project_repo
        .as_ref()
        .create(&preexisting)
        .await
        .expect("seed insert");

    // Mock AI service should NOT be called
    let server = MockAiService::new().await;

    let app = test::init_service(
        App::new()
            .configure(config_app)
            .app_data(project_repo.clone())
            .app_data(web::Data::new(AiServiceClient::new(&server.url()))),
    )
    .await;

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(serde_json::json!({ "github_url": github_url }))
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), actix_web::http::StatusCode::OK);

    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 200);
    assert_eq!(msg.message, "Project already exists and is ready to use");
    assert!(msg.data.is_none());
}

#[actix_web::test]
async fn test_ingest_invalid_github_url_returns_bad_request() {
    let project_repo = init_db().await;

    // AI service should not be called for invalid URLs
    let server = MockAiService::new().await;

    let app = test::init_service(
        App::new()
            .configure(config_app)
            .app_data(project_repo.clone())
            .app_data(web::Data::new(AiServiceClient::new(&server.url()))),
    )
    .await;

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(serde_json::json!({ "github_url": "https://gitlab.com/owner/repo" })) // not github.com
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), actix_web::http::StatusCode::BAD_REQUEST);

    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 400);
    assert!(msg.message.starts_with("Invalid GitHub URL:"));
    assert!(msg.data.is_none());
}

#[rstest]
#[case::ai_service_500_error(500, r#"{"error": "Internal server error in AI service"}"#)]
#[case::ai_service_400_error(400, r#"{"error": "Repository not found or not accessible"}"#)]
#[case::ai_service_404_error(404, r#"{"error": "Repository not found or not accessible"}"#)]
#[actix_web::test]
async fn test_ingest_project_ai_service_errors(
    #[case] ai_status_code: usize,
    #[case] ai_response_body: &str,
) {
    let project_repo = init_db().await;

    let input_url = "https://github.com/TestOwner/TestRepo";
    let expected_canonical = "https://github.com/testowner/testrepo.git";

    // Mock AI service to return the specified error
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_error_ingest_mock(
        &mut mock_server,
        expected_canonical,
        ai_status_code,
        ai_response_body,
    );

    let ai_service_client = web::Data::new(AiServiceClient::new(&mock_server.url()));
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(serde_json::json!({ "github_url": input_url }))
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);

    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 500);
    assert_eq!(msg.message, "Internal server error");
    assert!(msg.data.is_none());

    mock.assert();

    // Check if project was stored based on expected behavior
    let stored_project = project_repo
        .as_ref()
        .find_by_github_url(expected_canonical)
        .await
        .expect("DB query failed");

    assert!(
        stored_project.is_none(),
        "Project should NOT be stored in DB"
    );
}

#[actix_web::test]
async fn test_ingest_project_ai_service_unavailable() {
    let project_repo = init_db().await;

    let input_url = "https://github.com/TestOwner/TestRepo";

    // Use an invalid URL to simulate AI service being completely unavailable
    let ai_service_client = web::Data::new(AiServiceClient::new("http://localhost:0"));
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(serde_json::json!({ "github_url": input_url }))
        .to_request();

    let response = test::call_service(&app, req).await;
    assert_eq!(response.status(), StatusCode::BAD_GATEWAY);

    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 502);
    assert_eq!(
        msg.message,
        "Upstream service error; please try again later"
    );
    assert!(msg.data.is_none());

    // Project should NOT be stored in DB when AI service is unavailable
    let expected_canonical = "https://github.com/testowner/testrepo.git";
    let stored_project = project_repo
        .as_ref()
        .find_by_github_url(expected_canonical)
        .await
        .expect("DB query failed");
    assert!(stored_project.is_none());
}
