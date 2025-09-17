/**
 * External API types used for communication with the backend
 */

export interface IngestRequest {
    github_url: string
}

export interface IngestResponse {
    canonical_github_url: string
}

export interface AnswerRequest {
    canonical_github_url?: string  // Optional for general vs project-specific questions
    question: string
}

export interface AnswerResponse {
    answer: string
}

export interface ApiResponse<T> {
    code: number
    data?: T
    message: string
}

// Type aliases for specific API responses
export type IngestApiResponse = ApiResponse<IngestResponse>
export type AnswerApiResponse = ApiResponse<AnswerResponse>
