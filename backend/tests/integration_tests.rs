use std::str;

use actix_web::{App, body::to_bytes, test};
use backend::app_config::config_app;
use serde_json::Value;

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

    // Parse the JSON response
    let json: Value = serde_json::from_str(body_str).expect("Response should be valid JSON");

    // Assert the structure and content
    assert_eq!(json["code"], 200);
    assert_eq!(json["message"], "API is healthy ✅");
    assert!(json["data"].is_null());
}
