use std::str;

use actix_web::{App, body::to_bytes, test};
use backend::app_config::config_app;

#[actix_web::test]
async fn test_health_check() {
    // Initialize the test server
    let app = test::init_service(App::new().configure(config_app)).await;

    // Make a GET request
    let req = test::TestRequest::get().uri("/health").to_request();

    // Call the service with the request
    let response = test::call_service(&app, req).await;

    // Assert the response
    assert_eq!(response.status(), actix_web::http::StatusCode::OK);
    let byte_sources = to_bytes(response.into_body()).await.unwrap();
    let body_str = str::from_utf8(&byte_sources).unwrap();
    assert_eq!(body_str, "API is healthy ✅");
}
