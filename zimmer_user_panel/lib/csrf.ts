let _csrf: string | null = null;
export function setCsrfToken(t: string | null) { _csrf = t; }
export function getCsrfToken(): string | null { return _csrf; }

export async function fetchCsrf(apiBase: string) {
  try {
    console.log('DEBUG: Fetching CSRF token from:', `${apiBase}/api/auth/csrf`);
    const res = await fetch(`${apiBase}/api/auth/csrf`, { 
      credentials: "include",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
    
    if (!res.ok) {
      console.warn('DEBUG: CSRF fetch failed with status:', res.status, res.statusText);
      return;
    }
    
    const data = await res.json().catch(() => ({}));
    if (data?.csrf_token) {
      setCsrfToken(data.csrf_token);
      console.log('DEBUG: CSRF token set successfully');
    } else {
      console.warn('DEBUG: No CSRF token in response:', data);
    }
  } catch (error) {
    console.warn('DEBUG: CSRF fetch error:', error);
    // Don't throw - this is not critical for app functionality
  }
}