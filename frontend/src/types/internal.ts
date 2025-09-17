/**
 * Internal frontend types for component state and props
 * These types are specific to the frontend implementation
 */

export interface GitHubUploadProps {
    onUploadSuccess?: (canonicalUrl: string) => void
    onUploadError?: (error: string) => void
}

// Chat-related types
export interface ChatMessage {
    id: string
    content: string
    sender: 'user' | 'ai'
    timestamp: Date
    isLoading?: boolean
}

export interface ChatState {
    messages: ChatMessage[]
    isLoading: boolean
    error: string | null
}

export interface ChatBoxProps {
    projectUrl?: string  // If provided, enables project-specific mode
    onError?: (error: string) => void
    onAddProject?: () => void  // For opening the project upload modal
    onRemoveProject?: () => void  // For removing the current project
}
