//! Internal API types for communication between Backend and AI Service
//!
//! These types define the contract for our backend service to communicate
//! with the AI service. They should not be exposed to external clients.

use serde::{Deserialize, Serialize};

/// Request payload for AI service repository ingestion
///
/// Sent to the AI service to trigger the ingestion and embedding process
/// for a GitHub repository.
#[derive(Serialize)]
pub(crate) struct AiServiceIngestRequest {
    /// The canonical GitHub repository URL to ingest
    ///
    /// Should always be in canonical format: `https://github.com/owner/repo.git`
    /// This URL will be used by the AI service to clone and process the repository.
    pub(crate) repo_url: String,
}

/// Request payload for AI service question answering
///
/// Sent to the AI service to get an AI-generated answer about a specific
/// repository using the ingested codebase as context.
#[derive(Serialize)]
pub(crate) struct AiServiceAnswerRequest {
    /// The canonical GitHub repository URL to query
    ///
    /// Must match a previously ingested repository in the AI service.
    pub(crate) repo_url: String,

    /// The user's question about the repository
    ///
    /// This field name matches the AI service's expected parameter name.
    pub(crate) user_question: String,
}

/// Response from AI service answer endpoint
///
/// Contains the AI-generated answer along with status information.
#[derive(Deserialize)]
pub(crate) struct AiServiceAnswerResponse {
    /// The AI-generated answer to the user's question
    ///
    /// This is the main response content that gets forwarded to the frontend.
    pub(crate) answer: String,
}
