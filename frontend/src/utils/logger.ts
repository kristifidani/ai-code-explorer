export function logError(error: unknown, context?: Record<string, unknown>): void {
    if (error instanceof Error) {
        console.error(error.message, {
            stack: error.stack,
            ...context,
        })
    } else {
        console.error('Unknown error', {
            error,
            ...context,
        })
    }
}

export function getErrorMessage(error: unknown): string {
    if (error instanceof Error) return error.message
    return 'Unexpected error occurred'
}