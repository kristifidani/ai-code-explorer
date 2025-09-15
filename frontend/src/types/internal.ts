/**
 * Internal frontend types for component state and props
 * These types are specific to the frontend implementation
 */

export interface UploadState {
    isLoading: boolean
    error: string | null
    success: boolean
    canonicalUrl: string | null
}

export interface GitHubUploadProps {
    onUploadSuccess?: (canonicalUrl: string) => void
    onUploadError?: (error: string) => void
}
