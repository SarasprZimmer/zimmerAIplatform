// Auth client utility for managing access tokens in memory
// Refresh tokens are handled by httpOnly cookies from the backend

let accessToken: string | null = null

export const authClient = {
  getAccessToken(): string | null {
    return accessToken
  },

  setAccessToken(token: string): void {
    accessToken = token
  },

  clearAccessToken(): void {
    accessToken = null
  },

  isAuthenticated(): boolean {
    return accessToken !== null
  }
}

// Helper function to attach Bearer token to headers
export function attachBearer(headers: HeadersInit = {}): HeadersInit {
  const token = authClient.getAccessToken()
  if (token) {
    return {
      ...headers,
      Authorization: `Bearer ${token}`
    }
  }
  return headers
}

// Helper function to redirect to login with reason
export function redirectToLogin(reason?: string): void {
  if (typeof window !== 'undefined') {
    const url = reason ? `/login?reason=${encodeURIComponent(reason)}` : '/login'
    window.location.href = url
  }
} 