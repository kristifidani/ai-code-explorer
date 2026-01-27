/**
 * External API types used for communication with the backend
 */

/// Ingestion
export interface IngestRequest {
    github_url: string
}

export interface IngestResponse {
    canonical_github_url: string
}

/// Answering
export interface AnswerRequest {
    canonical_github_url?: string  // Optional for general vs project-specific questions
    question: string
}

export interface AnswerResponse {
    answer: string
}

/// Project Listing
// Project entity returned from backend
export interface Project {
    canonical_github_url: string
    repo_name: string
}

// API response for project list
export type ProjectListApiResponse = ApiResponse<Project[]>

/// Generic API Response Wrapper
export interface ApiResponse<T> {
    code: number
    data?: T
    message: string
}

// Type aliases for specific API responses
export type IngestApiResponse = ApiResponse<IngestResponse>
export type AnswerApiResponse = ApiResponse<AnswerResponse>
