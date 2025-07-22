use actix_web::{HttpResponse, ResponseError, http::StatusCode};

pub type Result<T> = core::result::Result<T, Error>;

/// Placeholder for API errors
#[derive(thiserror::Error, Debug)]
pub enum Error {}

impl ResponseError for Error {
    fn status_code(&self) -> StatusCode {
        StatusCode::INTERNAL_SERVER_ERROR
    }

    /// Override error_response to return an empty response instead of the Display string
    fn error_response(&self) -> HttpResponse<actix_web::body::BoxBody> {
        HttpResponse::new(self.status_code())
    }
}
