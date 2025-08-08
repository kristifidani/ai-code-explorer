use actix_web::{HttpResponse, ResponseError, http::StatusCode};
use serde::Serialize;
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

// Error response body for API errors
#[derive(Serialize)]
struct ErrorResponseBody {
    code: u16,
    error: String,
}

impl Error {
    fn user_description(&self) -> String {
        match self {
            Error::MongoDBError(_) | Error::UnexpectedResponse { .. } | Error::Reqwest(_) => {
                "Internal server error".into()
            }
            Error::ProjectNotFound(msg) => format!("Project not found: {msg}"),
            Error::InvalidGithubUrl(msg) => format!("Invalid GitHub URL: {msg}"),
            Error::ParseError(_) => "Failed to parse the given input".into(),
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
            Error::InvalidGithubUrl(_) | Error::ParseError(_) | Error::Reqwest(_) => {
                StatusCode::BAD_REQUEST
            }
        }
    }

    fn error_response(&self) -> HttpResponse {
        let body = ErrorResponseBody {
            code: self.status_code().as_u16(),
            error: self.user_description(),
        };

        HttpResponse::build(self.status_code()).json(body)
    }
}
