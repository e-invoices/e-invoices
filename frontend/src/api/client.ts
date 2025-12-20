export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Helper to get auth headers
const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('access_token')
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// Flag to prevent multiple refresh attempts
let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb)
}

const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

// Refresh the access token using refresh token
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    return null
  }

  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) {
      // Refresh token expired or invalid - clear tokens
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      return null
    }

    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data.access_token
  } catch {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    return null
  }
}

// Generic API request function with automatic token refresh
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retry = true
): Promise<T> {
  const url = `${API_BASE}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  })

  // Handle 401 Unauthorized - try to refresh token
  if (response.status === 401 && retry) {
    if (!isRefreshing) {
      isRefreshing = true
      const newToken = await refreshAccessToken()
      isRefreshing = false

      if (newToken) {
        onTokenRefreshed(newToken)
        // Retry the original request with new token
        return apiRequest<T>(endpoint, options, false)
      } else {
        // Redirect to login or emit event
        window.dispatchEvent(new CustomEvent('auth:logout'))
        throw new Error('Session expired. Please log in again.')
      }
    } else {
      // Wait for the refresh to complete
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token: string) => {
          if (token) {
            resolve(apiRequest<T>(endpoint, options, false))
          } else {
            reject(new Error('Session expired'))
          }
        })
      })
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  // Handle 204 No Content - return undefined/null instead of trying to parse JSON
  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

// API methods
export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
}

export default api
