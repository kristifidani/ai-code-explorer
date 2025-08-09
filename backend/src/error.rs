use crate::types::response::ApiResponse;
use actix_web::{HttpResponse, ResponseError, http::StatusCode};
use url::ParseError;

pub type Result<T> = core::result::Result<T, Error>;

/// Placeholder for API errors
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("MongoDbError: {0}")]
    MongoDBError(#[from] mongodb::error::Error),
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
    ParseError(#[from] ParseError),
}

impl Error {
    fn user_description(&self) -> String {
        match self {
            Error::MongoDBError(_) | Error::UnexpectedResponse { .. } => {
                "Internal server error".into()
            }
            Error::ProjectNotFound(msg) => format!("Project not found: {msg}"),
            Error::InvalidGithubUrl(msg) => format!("Invalid GitHub URL: {msg}"),
            Error::ParseError(_) => "Failed to parse the given input".into(),
            Error::Reqwest(_) => "Upstream service error; please try again later".into(),
        }
    }
}

impl ResponseError for Error {
    fn status_code(&self) -> StatusCode {
        match self {
            Error::MongoDBError(_) | Error::UnexpectedResponse { code: _, body: _ } => {
                StatusCode::INTERNAL_SERVER_ERROR
            }
            Error::ProjectNotFound(_) => StatusCode::NOT_FOUND,
            Error::InvalidGithubUrl(_) | Error::ParseError(_) => StatusCode::BAD_REQUEST,
            Error::Reqwest(_) => StatusCode::BAD_GATEWAY,
        }
    }

    fn error_response(&self) -> HttpResponse {
        ApiResponse::<()>::new(self.status_code(), None, &self.user_description()).into_response()
    }
}
