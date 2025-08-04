use actix_web::{HttpResponse, ResponseError, http::StatusCode};

pub type Result<T> = core::result::Result<T, Error>;

/// Placeholder for API errors
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("MongoDbError: {0}")]
    MongoDBError(mongodb::error::Error),
    #[error("Invalid project id: {0}")]
    InvalidProjectId(String),
    #[error("Project not found: {0}")]
    ProjectNotFound(String),
}

impl ResponseError for Error {
    fn status_code(&self) -> StatusCode {
        match self {
            Error::MongoDBError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Error::InvalidProjectId(_) => StatusCode::BAD_REQUEST,
            Error::ProjectNotFound(_) => StatusCode::NOT_FOUND,
        }
    }

    /// Override error_response to return an empty response instead of the Display string
    fn error_response(&self) -> HttpResponse<actix_web::body::BoxBody> {
        HttpResponse::new(self.status_code())
    }
}
