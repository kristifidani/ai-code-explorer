//! External API types for communication between Frontend and Backend
//!

use crate::error::{Result, ValidationError};
use serde::{Deserialize, Serialize};

/// Request to ingest a GitHub repository
#[derive(Deserialize, Serialize)]
pub struct IngestRequest {
    /// The GitHub repository URL to ingest
    pub github_url: url::Url,
}

/// Response from successful repository ingestion
#[derive(Serialize, Deserialize)]
pub struct IngestResponse {
    /// The canonicalized GitHub repository URL always in the format: `https://github.com/owner/repo.git`
    pub canonical_github_url: url::Url,
}

/// Request to ask a question with optional project context
#[derive(Deserialize, Serialize)]
#[cfg_attr(test, derive(Debug))]
pub struct AnswerRequest {
    /// Optional canonical GitHub repository URL (from IngestResponse)
    pub canonical_github_url: Option<url::Url>,

    /// The question to ask
    pub question: String,
}

impl AnswerRequest {
    /// Maximum allowed length for a question (in characters)
    const MAX_QUESTION_LENGTH: usize = 2000;

    /// Create a new AnswerRequest with comprehensive validation.
    ///
    /// Validates:
    /// - Trims whitespace
    /// - Rejects empty questions
    /// - Enforces length limits
    /// - Checks for invalid control characters
    /// - Handles optional GitHub URL for general vs project-specific questions
    pub fn new(canonical_github_url: Option<url::Url>, question: String) -> Result<Self> {
        let trimmed = question.trim();

        // Check for empty input
        if trimmed.is_empty() {
            return Err(ValidationError::EmptyInput(
                "Question cannot be empty".to_string(),
            ))?;
        }

        // Check length limit
        if trimmed.len() > Self::MAX_QUESTION_LENGTH {
            return Err(ValidationError::InputTooLong(format!(
                "Question must be {} characters or less, got {}",
                Self::MAX_QUESTION_LENGTH,
                trimmed.len()
            )))?;
        }

        // Check for control characters (except newlines and tabs which are OK for questions)
        if trimmed
            .chars()
            .any(|c| c.is_control() && c != '\n' && c != '\t')
        {
            return Err(ValidationError::InvalidCharacters(
                "Question contains invalid control characters".to_string(),
            ))?;
        }

        Ok(AnswerRequest {
            canonical_github_url,
            question: trimmed.to_string(),
        })
    }
}

/// Response containing the AI-generated answer
#[derive(Serialize, Deserialize)]
pub struct AnswerResponse {
    /// The AI-generated answer to the user's question
    pub answer: String,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::error::{Error, ValidationError};
    use rstest::rstest;
    use url::Url;

    fn test_url() -> Url {
        Url::parse("https://github.com/owner/repo.git").unwrap()
    }

    #[rstest]
    #[case("Valid question")]
    #[case("What is this repository about?")]
    #[case("How does the authentication work?\nCan you explain?")]
    #[case("Question with\ttabs")]
    #[case(&"a".repeat(2000))] // Exactly at limit
    #[case("  Valid question with spaces  ")]
    #[case("\n\tQuestion with whitespace\n\t")]
    #[case("   Multiple   spaces   inside   ")]
    fn test_valid_questions(#[case] question: &str) {
        let result = AnswerRequest::new(Some(test_url()), question.to_string());

        let request = result.unwrap();
        assert_eq!(request.question, question.trim());
        assert_eq!(request.canonical_github_url, Some(test_url()));
    }

    #[rstest]
    #[case("")]
    #[case("   ")]
    #[case("\n\t  \n")]
    fn test_empty_input_validation(#[case] question: &str) {
        let result = AnswerRequest::new(Some(test_url()), question.to_string());

        assert!(matches!(
            result.unwrap_err(),
            Error::ValidationError(ValidationError::EmptyInput(_))
        ));
    }

    #[rstest]
    #[case(&"a".repeat(2001))] // Just over limit
    #[case(&"a".repeat(5000))] // Way over limit
    fn test_length_validation(#[case] question: &str) {
        let result = AnswerRequest::new(Some(test_url()), question.to_string());

        assert!(matches!(
            result.unwrap_err(),
            Error::ValidationError(ValidationError::InputTooLong(_))
        ));
    }

    #[rstest]
    #[case("Question with \x00 null byte")]
    #[case("Question with \x01 control char")]
    #[case("Question with \x1F control char")]
    #[case("Question with \x7F delete char")]
    fn test_control_character_validation(#[case] question: &str) {
        let result = AnswerRequest::new(Some(test_url()), question.to_string());

        assert!(matches!(
            result.unwrap_err(),
            Error::ValidationError(ValidationError::InvalidCharacters(_))
        ));
    }

    #[rstest]
    #[case("General programming question")]
    #[case("What are best practices for Rust?")]
    #[case("How do I implement a REST API?")]
    fn test_general_questions(#[case] question: &str) {
        let result = AnswerRequest::new(None, question.to_string());

        let request = result.unwrap();
        assert_eq!(request.question, question.trim());
        assert_eq!(request.canonical_github_url, None);
    }

    #[test]
    fn test_general_question_empty_validation() {
        let result = AnswerRequest::new(None, "".to_string());

        assert!(matches!(
            result.unwrap_err(),
            Error::ValidationError(ValidationError::EmptyInput(_))
        ));
    }
}
