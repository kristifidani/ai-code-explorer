/**
 * External API types used for communication with the backend
 */

export interface IngestRequest {
    github_url: string
}

export interface IngestResponse {
    canonical_github_url: string
}

export interface ApiResponse<T> {
    code: number
    data?: T
    message: string
}

// Type alias for the specific API response we use
export type IngestApiResponse = ApiResponse<IngestResponse>
