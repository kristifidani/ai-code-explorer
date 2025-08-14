use actix_web::{App, test};
use backend::{app_config::config_app, types::response::ApiResponse};

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
