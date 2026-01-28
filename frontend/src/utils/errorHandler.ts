// Centralized error handling utility

export interface ErrorContext {
    component: string;
    action?: string;
}

export interface AppError {
    message: string;
    context: ErrorContext;
    originalError?: unknown;
}

export function handleError(
    message: string,
    context: ErrorContext,
    originalError?: unknown
): AppError {
    console.error(`[${message}]`, context, originalError);
    return { message, context, originalError };
}
