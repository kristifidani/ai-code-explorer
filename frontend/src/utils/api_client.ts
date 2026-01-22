/**
 * Extract a tiny API helper for backend calls to avoid fetch duplication
 */

export async function backendApiWrapper<TRequest, TResponse>(
    method: string,
    url: string,
    body: TRequest
): Promise<TResponse> {
    const response = await fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify(body),
    })

    const json = (await response.json()) as unknown

    console.info('[Frontend] Received response from backend:', {
        status: response.status,
        ok: response.ok,
    })

    if (!response.ok) {
        const apiResponse = json as { message?: string }
        const errorMessage = apiResponse.message || `HTTP ${response.status}`
        throw new Error(errorMessage)
    }

    return json as TResponse
}
