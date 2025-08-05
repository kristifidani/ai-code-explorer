use actix_web::{HttpResponse, ResponseError, http::StatusCode};
use url::ParseError;

pub type Result<T> = core::result::Result<T, Error>;

/// Placeholder for API errors
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("MongoDbError: {0}")]
    MongoDBError(mongodb::error::Error),
    #[error("Project not found: {0}")]
    ProjectNotFound(String),
    #[error("Invalid GitHub URL: {0}")]
    InvalidGithubUrl(String),
    #[error("Reqwest error: {0}")]
    Reqwest(#[from] reqwest::Error),
    #[error("Unexpected response: code: {code}, body: {body}")]
    UnexpectedResponse {
        code: reqwest::StatusCode,
        body: String,
    },
    #[error("Parse error: {0}")]
    ParseError(ParseError),
}

impl ResponseError for Error {
    fn status_code(&self) -> StatusCode {
        match self {
            Error::MongoDBError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Error::ProjectNotFound(_) => StatusCode::NOT_FOUND,
            Error::InvalidGithubUrl(_) => StatusCode::BAD_REQUEST,
            Error::Reqwest(_) => StatusCode::BAD_REQUEST,
            Error::UnexpectedResponse { code: _, body: _ } => StatusCode::INTERNAL_SERVER_ERROR,
            Error::ParseError(_) => StatusCode::BAD_REQUEST,
        }
    }

    /// Override error_response to return an empty response instead of the Display string
    fn error_response(&self) -> HttpResponse<actix_web::body::BoxBody> {
        HttpResponse::new(self.status_code())
    }
}
