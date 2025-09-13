let _csrf: string | null = null;
export function setCsrfToken(t: string | null) { _csrf = t; }
export function getCsrfToken(): string | null { return _csrf; }

export async function fetchCsrf(apiBase: string) {
  const res = await fetch(`${apiBase}/api/auth/csrf`, { credentials: "include" });
  if (!res.ok) return;
  const data = await res.json().catch(()=> ({}));
  if (data?.csrf_token) setCsrfToken(data.csrf_token);
}