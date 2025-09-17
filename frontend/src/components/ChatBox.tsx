import { useState, useRef, useEffect } from 'react'
import MarkdownIt from 'markdown-it'
import type {
    AnswerRequest,
    AnswerApiResponse,
} from '../types/external'
import type {
    ChatMessage,
    ChatState,
    ChatBoxProps
} from '../types/internal'

// Backend API endpoint from environment
const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL as string

// Configure markdown-it for better formatting
const md = new MarkdownIt({
    breaks: true,
    html: false,
    linkify: false,
    typographer: false
})

// Custom renderer for consistent spacing
md.renderer.rules.paragraph_open = () => '<p style="margin: 0 0 0.5rem 0;">'
md.renderer.rules.paragraph_close = () => '</p>'
md.renderer.rules.bullet_list_open = () => '<ul style="margin: 0.5rem 0; padding-left: 1.2rem; list-style-type: disc;">'
md.renderer.rules.bullet_list_close = () => '</ul>'
md.renderer.rules.list_item_open = () => '<li style="margin: 0.1rem 0;">'
md.renderer.rules.list_item_close = () => '</li>'

export function ChatBox({
    projectUrl,
    onError,
    onAddProject,
    onRemoveProject
}: ChatBoxProps) {
    const [input, setInput] = useState('')
    const [state, setState] = useState<ChatState>({
        messages: [],
        isLoading: false,
        error: null,
    })

    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [state.messages])

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus()
    }, [])

    const addMessage = (content: string, sender: 'user' | 'ai', isLoading = false): string => {
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`
        const message: ChatMessage = {
            id: messageId,
            content,
            sender,
            timestamp: new Date(),
            isLoading,
        }

        setState(prev => ({
            ...prev,
            messages: [...prev.messages, message],
        }))

        return messageId
    }

    const updateMessage = (messageId: string, content: string, isLoading = false) => {
        setState(prev => ({
            ...prev,
            messages: prev.messages.map(msg =>
                msg.id === messageId
                    ? { ...msg, content, isLoading }
                    : msg
            ),
        }))
    }

    const handleError = (error: unknown, aiMessageId: string) => {
        const errorMessage = error instanceof Error ? error.message : 'Network error occurred'
        setState(prev => ({
            ...prev,
            error: errorMessage,
            messages: prev.messages.filter(msg => msg.id !== aiMessageId)
        }))
        onError?.(errorMessage)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!input.trim() || state.isLoading) return

        if (!BACKEND_API_URL) {
            const errorMessage = 'Backend URL is not configured (VITE_BACKEND_API_URL).'
            setState(prev => ({ ...prev, error: errorMessage }))
            onError?.(errorMessage)
            return
        }

        const userMessage = input.trim()
        setInput('')

        // Add user message
        addMessage(userMessage, 'user')

        // Add loading AI message
        const aiMessageId = addMessage('Thinking ...', 'ai', true)

        setState(prev => ({ ...prev, isLoading: true, error: null }))

        try {
            const requestBody: AnswerRequest = {
                question: userMessage,
                ...(projectUrl && { canonical_github_url: projectUrl })
            }

            const endpoint = new URL('/v1/answer', BACKEND_API_URL).toString()
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(requestBody),
            })

            const result = await response.json() as AnswerApiResponse

            if (response.ok && result.data) {
                updateMessage(aiMessageId, result.data.answer)
            } else {
                const errorMessage = result.message || 'Failed to get answer'
                handleError(new Error(errorMessage), aiMessageId)
            }
        } catch (error) {
            handleError(error, aiMessageId)
        } finally {
            setState(prev => ({ ...prev, isLoading: false }))
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            void handleSubmit(e as unknown as React.FormEvent)
        }
    }

    return (
        <div className="max-w-6xl mx-auto h-[700px] bg-white border border-gray-200 rounded-lg shadow-lg flex flex-col">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            AI Assistant
                        </h2>
                        <p className="text-sm text-gray-600">
                            {projectUrl
                                ? `Ask questions about: ${projectUrl}`
                                : 'Ask me anything about programming, software development, or general topics'
                            }
                        </p>
                    </div>
                    <div className="flex items-center space-x-3">
                        {projectUrl ? (
                            <>
                                <div className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                                    Project Mode
                                </div>
                                <button
                                    onClick={onRemoveProject}
                                    className="px-3 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full hover:bg-red-200 transition-colors"
                                    title="Remove project context"
                                >
                                    ✕
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={onAddProject}
                                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                            >
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                                Add Project
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6" style={{
                scrollbarWidth: 'thin',
                scrollbarColor: '#cbd5e1 #f1f5f9'
            }}>
                {state.messages.length === 0 && (
                    <div className="text-center py-12">
                        <div className="w-16 h-16 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-medium text-gray-900 mb-3">
                            Start a conversation
                        </h3>
                        <p className="text-gray-500 text-base max-w-md mx-auto">
                            {projectUrl
                                ? 'Ask me anything about the uploaded project - code structure, implementation details, architecture, etc.'
                                : 'Ask me about programming concepts, best practices, or any technical questions you have.'
                            }
                        </p>
                    </div>
                )}

                {state.messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[75%] px-5 py-4 rounded-2xl ${message.sender === 'user'
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'bg-gray-100 text-gray-900 shadow-sm border border-gray-200'
                                }`}
                        >
                            {message.isLoading ? (
                                <div className="flex items-center space-x-3">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                    </div>
                                    <span className="text-sm text-gray-600">Thinking...</span>
                                </div>
                            ) : (
                                <div
                                    className="whitespace-pre-wrap break-words leading-relaxed chat-message"
                                    dangerouslySetInnerHTML={{
                                        __html: message.sender === 'ai' ? md.render(message.content) : message.content
                                    }}
                                />
                            )}
                            <div className={`text-xs mt-3 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                                }`}>
                                {message.timestamp.toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Show error messages differently */}
                {state.error && (
                    <div className="flex justify-center">
                        <div className="max-w-[75%] px-5 py-4 rounded-2xl bg-red-50 border border-red-200 text-red-800">
                            <div className="flex items-center space-x-2">
                                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="font-medium">Error:</span>
                            </div>
                            <div className="mt-1 text-sm">
                                {state.error}
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <div className="border-t border-gray-200 p-6 bg-gray-50">
                <form onSubmit={(e) => { void handleSubmit(e) }} className="flex space-x-4">
                    <div className="flex-1">
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={projectUrl
                                ? "Ask about the code, architecture, implementation..."
                                : "Ask me anything..."
                            }
                            className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 resize-none shadow-sm bg-white"
                            rows={3}
                            disabled={state.isLoading}
                        />
                        <div className="mt-2 text-xs text-gray-500 flex justify-between">
                            <span>Press Enter to send, Shift+Enter for new line</span>
                            <span className={input.length > 500 ? 'text-orange-500' : ''}>
                                {input.length}/1000
                            </span>
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={!input.trim() || state.isLoading}
                        className="px-6 py-4 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm self-start"
                    >
                        {state.isLoading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                    </button>
                </form>
            </div>
        </div>
    )
}
