function stripLeadingSlash(value: string): string {
    return value.startsWith('/') ? value.slice(1) : value
}

function stripTrailingSlash(value: string): string {
    return value.endsWith('/') ? value.slice(0, -1) : value
}

function ensureLeadingSlash(value: string): string {
    if (!value) return '/'
    return value.startsWith('/') ? value : `/${value}`
}

function joinPathPrefix(prefix: string, endpoint: string): string {
    const normalizedPrefix = stripTrailingSlash(ensureLeadingSlash(prefix))
    const normalizedEndpoint = ensureLeadingSlash(endpoint)

    if (!normalizedPrefix || normalizedPrefix === '/') {
        return normalizedEndpoint
    }

    return `${normalizedPrefix}/${stripLeadingSlash(normalizedEndpoint)}`
}

/**
 * Builds a backend endpoint URL suitable for fetch().
 *
 * `VITE_BACKEND_API_URL` is injected by Vite at build time and may be:
 * - Absolute URL (local dev): "http://localhost:8080"
 * - Absolute URL with path prefix: "https://example.com/api"
 * - Relative path prefix (production behind nginx): "/api"
 *
 * Examples:
 * - buildApiUrl("http://localhost:8080", "/v1/answer") => "http://localhost:8080/v1/answer"
 * - buildApiUrl("https://example.com/api", "/v1/answer") => "https://example.com/api/v1/answer"
 * - buildApiUrl("/api", "/v1/answer") => "/api/v1/answer"
 */
export function buildApiUrl(base: string, endpointPath: string): string {
    const trimmedBase = base.trim()
    if (!trimmedBase) {
        throw new Error('Backend URL is not configured (VITE_BACKEND_API_URL).')
    }

    const endpoint = ensureLeadingSlash(endpointPath.trim())

    // Relative base ("/api") => return a relative URL suitable for same-origin fetch()
    if (trimmedBase.startsWith('/')) {
        return joinPathPrefix(trimmedBase, endpoint)
    }

    // Absolute base => preserve origin and treat any pathname as a prefix
    const parsedBase = new URL(trimmedBase)
    const basePrefix = parsedBase.pathname === '/' ? '' : stripTrailingSlash(parsedBase.pathname)
    const fullPath = joinPathPrefix(basePrefix, endpoint)

    return `${parsedBase.origin}${fullPath}`
}
