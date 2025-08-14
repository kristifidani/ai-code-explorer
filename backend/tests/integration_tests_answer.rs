mod utils;

use actix_web::{App, http::StatusCode, test, web};
use backend::{
    app_config::config_app,
    clients::{ai_service_client::AiServiceClient, db::ProjectRepositoryImpl},
    types::{
        entities::ProjectEntity,
        external::{AnswerRequest, AnswerResponse},
        response::ApiResponse,
    },
};
use rstest::rstest;
use url::Url;
use utils::{MockAiService, init_db};

#[actix_web::test]
async fn test_answer_question_success() {
    // Init db
    let project_repo = init_db().await;

    // Pre-insert project in database
    let github_url = Url::parse("https://github.com/testowner/testrepo.git").unwrap();
    let preexisting = ProjectEntity::new_validated(&github_url).expect("valid canonical");
    project_repo
        .as_ref()
        .create(&preexisting)
        .await
        .expect("failed to pre-insert project");

    // QA
    let question = "What is this repository about?";
    let expected_answer =
        "This repository is a code analysis tool that helps developers understand codebases.";

    // Mock AI service
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_successful_answer_mock(
        &mut mock_server,
        "https://github.com/testowner/testrepo.git",
        question,
        expected_answer,
    );
    let server_url = Url::parse(&mock_server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo)
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/answer")
        .set_json(&AnswerRequest {
            canonical_github_url: preexisting.canonical_github_url,
            question: question.to_string(),
        })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::OK);
    let msg: ApiResponse<AnswerResponse> = test::read_body_json(response).await;
    assert_eq!(msg.code, 200);
    assert_eq!(msg.message, "Question answered successfully");
    assert_eq!(msg.data.unwrap().answer, expected_answer);

    mock.assert();
}

#[actix_web::test]
async fn test_answer_question_project_not_found() {
    // Init db
    let project_repo = init_db().await;

    // DO NOT pre-insert project - it should not exist
    let github_url = Url::parse("https://github.com/nonexistent/repo.git").unwrap();
    let question = "What is this repository about?";

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
        .uri("/v1/answer")
        .set_json(&AnswerRequest {
            canonical_github_url: github_url,
            question: question.to_string(),
        })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 404);
    assert_eq!(
        msg.message,
        "Project not found. Please ingest a project first."
    );
    assert!(msg.data.is_none());
}

#[rstest]
#[case("", "Empty input: Question cannot be empty")]
#[case("   ", "Empty input: Question cannot be empty")]
#[case(&"a".repeat(2001), "Input too long: Question must be 2000 characters or less")]
#[case(
    "Question with \x00 null byte",
    "Invalid characters: Question contains invalid control characters"
)]
#[actix_web::test]
async fn test_answer_question_invalid_input(
    #[case] question: &str,
    #[case] expected_error_message: &str,
) {
    // Init db
    let project_repo = init_db().await;

    let github_url = Url::parse("https://github.com/testowner/testrepo.git").unwrap();

    // Mock AI service should NOT be called due to validation failure
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
        .uri("/v1/answer")
        .set_json(&AnswerRequest {
            canonical_github_url: github_url,
            question: question.to_string(),
        })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::BAD_REQUEST);
    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 400);
    assert!(msg.message.contains(expected_error_message));
    assert!(msg.data.is_none());
}

#[rstest]
#[case::ai_service_500_error(500, r#"{"error": "Internal server error in AI service"}"#)]
#[case::ai_service_400_error(400, r#"{"error": "Invalid question format"}"#)]
#[case::ai_service_404_error(404, r#"{"error": "Project not found in AI service"}"#)]
#[actix_web::test]
async fn test_answer_question_ai_service_errors(
    #[case] ai_status_code: usize,
    #[case] ai_response_body: &str,
) {
    // Init db and pre insert project
    let project_repo = init_db().await;
    let github_url = Url::parse("https://github.com/testowner/testrepo.git").unwrap();
    let preexisting = ProjectEntity::new_validated(&github_url).expect("valid canonical");
    project_repo
        .as_ref()
        .create(&preexisting)
        .await
        .expect("seed insert");

    let question = "What is this repository about?";

    // Mock AI service to return the specified error
    let mut mock_server = MockAiService::new().await;
    let mock = MockAiService::create_error_answer_mock(
        &mut mock_server,
        "https://github.com/testowner/testrepo.git",
        question,
        ai_status_code,
        ai_response_body,
    );
    let server_url = Url::parse(&mock_server.url()).unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(server_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo)
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/answer")
        .set_json(&AnswerRequest {
            canonical_github_url: github_url,
            question: question.to_string(),
        })
        .to_request();

    let response = test::call_service(&app, req).await;

    // Assert
    assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    let msg: ApiResponse<()> = test::read_body_json(response).await;
    assert_eq!(msg.code, 500);
    assert_eq!(msg.message, "Internal server error");
    assert!(msg.data.is_none());

    mock.assert();
}

#[actix_web::test]
async fn test_answer_question_ai_service_unavailable() {
    // Init db and pre insert project
    let project_repo = init_db().await;
    let github_url = Url::parse("https://github.com/testowner/testrepo.git").unwrap();
    let preexisting = ProjectEntity::new_validated(&github_url).expect("valid canonical");
    project_repo
        .as_ref()
        .create(&preexisting)
        .await
        .expect("seed insert");

    let question = "What is this repository about?";

    // Use an invalid URL to simulate AI service being completely unavailable
    let invalid_service_url = Url::parse("http://localhost:0").unwrap();
    let ai_service_client = web::Data::new(AiServiceClient::new(invalid_service_url));

    // Init test app
    let app = test::init_service(
        App::new()
            .app_data(project_repo)
            .app_data(ai_service_client)
            .configure(config_app),
    )
    .await;

    // Make call
    let req = test::TestRequest::post()
        .uri("/v1/answer")
        .set_json(&AnswerRequest {
            canonical_github_url: github_url,
            question: question.to_string(),
        })
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
}
