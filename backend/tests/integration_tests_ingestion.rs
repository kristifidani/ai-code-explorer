mod utils;

use actix_web::{App, http::StatusCode, test, web};
use backend::{
    app_config::config_app,
    clients::{ai_service_client::AiServiceClient, db::ProjectRepositoryImpl},
    types::{
        entities::ProjectEntity,
        external::{IngestRequest, IngestResponse},
        response::ApiResponse,
    },
};
use rstest::rstest;
use url::Url;
use utils::{MockAiService, init_db};

#[actix_web::test]
async fn test_ingest_project_success() {
    // Init db
    let project_repo = init_db().await;

    // Setup urls
    let github_url =
        Url::parse("https://github.com/TestOwner/TestRepo").expect("invalid input url");
    let expected_canonical = ProjectEntity::new_validated(&github_url)
        .expect("invalid url")
        .canonical_github_url;

    // Mock AI service
    let mut mock_server = MockAiService::new().await;
    let mock =
        MockAiService::create_successful_ingest_mock(&mut mock_server, expected_canonical.as_str());
    let server_url = Url::parse(&mock_server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&IngestRequest { github_url })
        .to_request();
    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), actix_web::http::StatusCode::CREATED);
    let msg: ApiResponse<IngestResponse> = test::read_body_json(response).await;
    assert_eq!(msg.code, 201);
    assert_eq!(msg.message, "Project ingested successfully");
    assert_eq!(msg.data.unwrap().canonical_github_url, expected_canonical);

    mock.assert();

    // Followup check db
    let stored_project = project_repo
        .find_by_canonical_github_url(&expected_canonical)
        .await
        .expect("DB query failed")
        .expect("Project should exist in DB");
    assert_eq!(stored_project.canonical_github_url, expected_canonical);
}

#[actix_web::test]
async fn test_ingest_project_already_exists() {
    // Init db and pre-insert project
    let project_repo = init_db().await;

    let github_url = Url::parse("https://github.com/Already/Exists").unwrap();
    let project_entity = ProjectEntity::new_validated(&github_url).expect("invalid canonical");
    project_repo
        .create(&project_entity)
        .await
        .expect("failed to pre-insert url");

    // Mock AI service should NOT be called
    let server = MockAiService::new().await;
    let server_url = Url::parse(&server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .configure(config_app)
            .app_data(project_repo)
            .app_data(ai_service_client),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&IngestRequest { github_url })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), actix_web::http::StatusCode::CONFLICT);
    let msg: ApiResponse<IngestResponse> = test::read_body_json(response).await;
    assert_eq!(msg.code, 409);
    assert_eq!(msg.message, "Project already exists and is ready to use");
    assert_eq!(
        msg.data.unwrap().canonical_github_url,
        project_entity.canonical_github_url
    );
}

#[actix_web::test]
async fn test_ingest_invalid_github_url_returns_bad_request() {
    // Init db
    let project_repo = init_db().await;

    // AI service should not be called for invalid URLs
    let server = MockAiService::new().await;
    let server_url = Url::parse(&server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .configure(config_app)
            .app_data(project_repo)
            .app_data(ai_service_client),
    )
    .await;

    // Make call
    let invalid_url = Url::parse("https://gitlab.com/owner/repo").unwrap(); // not github.com
    let request_body = IngestRequest {
        github_url: invalid_url,
    };

    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&request_body)
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
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
    // Init db
    let project_repo = init_db().await;

    // Used urls
    let github_url = Url::parse("https://github.com/TestOwner/TestRepo").unwrap();
    let expected_canonical = ProjectEntity::new_validated(&github_url)
        .expect("invalid url")
        .canonical_github_url;

    // Mock AI service to return the specified error
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_error_ingest_mock(
        &mut mock_server,
        expected_canonical.as_str(),
        ai_status_code,
        ai_response_body,
    );
    let server_url = Url::parse(&mock_server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&IngestRequest { github_url })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 500);
    assert_eq!(msg.message, "Internal server error");
    assert!(msg.data.is_none());

    mock.assert();

    // Post db check should not store
    let stored_project = project_repo
        .find_by_canonical_github_url(&expected_canonical)
        .await
        .expect("DB query failed");

    assert!(
        stored_project.is_none(),
        "Project should NOT be stored in DB"
    );
}

#[actix_web::test]
async fn test_ingest_project_ai_service_unavailable() {
    // Init db
    let project_repo = init_db().await;

    // Used urls
    let github_url = Url::parse("https://github.com/TestOwner/TestRepo").unwrap();
    let expected_canonical = ProjectEntity::new_validated(&github_url)
        .expect("invalid url")
        .canonical_github_url;

    // Use an invalid URL to simulate AI service being completely unavailable
    let invalid_service_url = Url::parse("http://localhost:0").unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(invalid_service_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo.clone())
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/ingest")
        .set_json(&IngestRequest { github_url })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::BAD_GATEWAY);
    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 502);
    assert_eq!(
        msg.message,
        "Upstream service error; please try again later"
    );
    assert!(msg.data.is_none());

    // Project should NOT be stored in DB when AI service is unavailable
    let stored_project = project_repo
        .find_by_canonical_github_url(&expected_canonical)
        .await
        .expect("DB query failed");
    assert!(stored_project.is_none());
}
