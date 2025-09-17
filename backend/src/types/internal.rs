//! Internal API types for communication between Backend and AI Service
//!
//! They should not be exposed to external clients.

use serde::{Deserialize, Serialize};

/// Request payload for AI service repository ingestion
#[derive(Serialize)]
pub(crate) struct AiServiceIngestRequest {
    /// The canonical GitHub repository URL to ingest with format: `https://github.com/owner/repo.git`
    pub(crate) canonical_github_url: url::Url,
}

/// Request payload for AI service question answering with optional
/// repository context for project-specific or general questions.
#[derive(Serialize)]
pub(crate) struct AiServiceAnswerRequest {
    /// Optional canonical GitHub repository URL for context
    pub(crate) canonical_github_url: Option<url::Url>,

    /// The user's question
    pub(crate) user_question: String,
}

/// Response from AI service answer endpoint
#[derive(Deserialize)]
pub(crate) struct AiServiceAnswerResponse {
    /// The AI-generated answer to the user's question
    pub(crate) answer: String,
}
