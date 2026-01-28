/**
 * Extract a tiny API helper for backend calls to avoid fetch duplication
 */

export async function backendApiWrapper<TRequest, TResponse>(
    method: string,
    url: string,
    body?: TRequest,
    signal?: AbortSignal
): Promise<TResponse> {
    const response = await fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        ...(body !== undefined && { body: JSON.stringify(body) }),
        ...(signal ? { signal } : {}),
    })

    const json = (await response.json()) as unknown

    console.info('[Frontend] Received response from backend:', {
        url,
        status_code: response.status,
        status_text: response.statusText,
    })

    if (!response.ok) {
        const apiResponse = json as { message?: string }
        const errorMessage = apiResponse.message || `HTTP ${response.status}`
        throw new Error(errorMessage)
    }

    return json as TResponse
}
