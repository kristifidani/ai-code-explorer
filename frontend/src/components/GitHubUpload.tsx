import { useState } from 'react'
import type {
    IngestRequest,
    IngestApiResponse,
} from '../types/external'
import type {
    GitHubUploadProps
} from '../types/internal'
import { buildApiUrl } from '../utils/api_url_builder'
import { postJson } from '../utils/api_client'
import { getErrorMessage, logError } from '../utils/logger'

export function GitHubUpload({ onUploadSuccess, onUploadError }: GitHubUploadProps) {
    const [githubUrl, setGithubUrl] = useState('')
    const [state, setState] = useState({
        isLoading: false,
        error: null as string | null,
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        // Note: GitHub URL validation is handled by the backend
        // Frontend validation could be added here if needed for better UX

        setState(prev => ({ ...prev, isLoading: true, error: null }))

        try {
            const requestBody: IngestRequest = {
                github_url: githubUrl
            }

            const endpoint = buildApiUrl('/v1/ingest')
            console.info('[Frontend] Sending ingest request to backend:', {
                endpoint,
                githubUrl
            })

            const result = await postJson<IngestRequest, IngestApiResponse>(
                endpoint,
                requestBody
            )

            if (!result.data) {
                throw new Error(result.message ?? 'Backend returned no data')
            }

            onUploadSuccess?.(result.data.canonical_github_url)
            setState(prev => ({ ...prev, isLoading: false }))

        } catch (error) {
            logError(error, { component: 'GitHubUpload', githubUrl })
            const message = getErrorMessage(error)
            setState(prev => ({ ...prev, isLoading: false, error: message }))
            onUploadError?.(message)
        }
    }

    return (
        <div>
            <form onSubmit={(e) => { void handleSubmit(e) }} className="space-y-4">
                <div>
                    <label htmlFor="githubUrl" className="block text-sm font-medium text-gray-700 mb-2">
                        GitHub Repository URL
                    </label>
                    <input
                        type="url"
                        id="githubUrl"
                        value={githubUrl}
                        onChange={(e) => setGithubUrl(e.target.value)}
                        placeholder="https://github.com/owner/repository"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={state.isLoading}
                        required
                    />
                </div>

                {state.error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-700">{state.error}</p>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={state.isLoading}
                    className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {state.isLoading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span className="sr-only">Uploading...</span>
                        </span>
                    ) : (
                        'Upload Project'
                    )}
                </button>
            </form>
        </div>
    )
}
