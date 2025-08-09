use actix_web::{HttpResponse, http::StatusCode};
use serde::Serialize;

/// Unified API Response structure
/// Provides consistent format for all API responses
#[derive(Serialize)]
pub struct ApiResponse<T> {
    /// HTTP status code
    pub code: u16,
    /// Optional data payload
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<T>,
    /// Human-readable message
    pub message: String,
}

impl<T> ApiResponse<T>
where
    T: Serialize,
{
    pub fn new(code: StatusCode, data: Option<T>, message: &str) -> Self {
        Self {
            code: code.as_u16(),
            data,
            message: message.into(),
        }
    }

    /// Convert to HTTP response
    pub fn into_response(self) -> HttpResponse {
        let status_code =
            StatusCode::from_u16(self.code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);
        HttpResponse::build(status_code).json(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    #[derive(Serialize, PartialEq, Debug, Clone)]
    struct TestData {
        id: u32,
        name: String,
    }

    #[rstest]
    #[case(StatusCode::OK, "Success")]
    #[case(StatusCode::CREATED, "Created")]
    #[case(StatusCode::ACCEPTED, "Accepted")]
    fn test_response_with_data(#[case] status: StatusCode, #[case] message: &str) {
        let data = TestData {
            id: 1,
            name: "test".to_string(),
        };

        let response = ApiResponse::new(status, Some(data.clone()), message);

        assert_eq!(response.code, status.as_u16());
        assert_eq!(response.data, Some(data));
        assert_eq!(response.message, message);
    }

    #[rstest]
    #[case(StatusCode::OK, "Operation completed")]
    #[case(StatusCode::CREATED, "Resource created")]
    #[case(StatusCode::ACCEPTED, "Task accepted")]
    fn test_message_only_response(#[case] status: StatusCode, #[case] message: &str) {
        let response = ApiResponse::<()>::new(status, None, message);

        assert_eq!(response.code, status.as_u16());
        assert_eq!(response.data, None);
        assert_eq!(response.message, message);
    }

    #[rstest]
    #[case(StatusCode::BAD_REQUEST, "Invalid input")]
    #[case(StatusCode::NOT_FOUND, "Resource not found")]
    #[case(StatusCode::INTERNAL_SERVER_ERROR, "Server error")]
    fn test_error_response(#[case] status: StatusCode, #[case] message: &str) {
        let response = ApiResponse::<()>::new(status, None, message);

        assert_eq!(response.code, status.as_u16());
        assert_eq!(response.data, None);
        assert_eq!(response.message, message);
    }
}
