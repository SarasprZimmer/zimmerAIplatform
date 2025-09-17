import { redirect } from "next/navigation";
import { getAccessToken, setAccessToken } from "./authClient";
import { getCsrfToken, fetchCsrf } from "./csrf";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function refreshAccessToken(): Promise<boolean> {
  const res = await fetch(`${API}/api/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) return false;
  const j = await res.json().catch(()=>null);
  if (j?.access_token) {
    setAccessToken(j.access_token);
    return true;
  }
  return false;
}

export async function apiFetch(path: string, opts: RequestInit = {}): Promise<Response> {
  const headers = new Headers(opts.headers || {});
  // Use localStorage instead of in-memory storage to match main API client
  const access = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
  if (access) headers.set("Authorization", `Bearer ${access}`);

  // CSRF for unsafe methods
  const method = (opts.method || "GET").toUpperCase();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrf = getCsrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }

  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers,
    credentials: "include", // send cookies (refresh/CSRF)
  });

  // Auto-handle 401 (refresh path excluded)
  if (res.status === 401 && !path.includes("/auth/refresh")) {
    const ok = await refreshAccessToken();
    if (!ok) return res;
    const retryHeaders = new Headers(opts.headers || {});
    const access2 = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
    if (access2) retryHeaders.set("Authorization", `Bearer ${access2}`);
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      const csrf = getCsrfToken();
      if (csrf) retryHeaders.set("X-CSRF-Token", csrf);
    }
    return fetch(`${API}${path}`, {
      ...opts,
      headers: retryHeaders,
      credentials: "include",
    });
  }
  return res;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API}/api/auth/login`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  if (res.status === 401) {
    // maybe otp_required
    const j = await res.json().catch(()=>null);
    throw { status: 401, data: j };
  }
  if (!res.ok) throw new Error("login_failed");
  const j = await res.json();
  if (j?.access_token) {
    setAccessToken(j.access_token);
    // Also store in localStorage to match main API client
    if (typeof window !== 'undefined') {
      localStorage.setItem("access_token", j.access_token);
    }
  }
  return j;
}

export async function verifyOtp(challenge_token: string, otp_code: string) {
  const res = await fetch(`${API}/api/auth/2fa/verify`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    credentials: "include",
    body: JSON.stringify({ challenge_token, otp_code })
  });
  if (!res.ok) throw new Error("otp_failed");
  const j = await res.json();
  if (j?.access_token) {
    setAccessToken(j.access_token);
    // Also store in localStorage to match main API client
    if (typeof window !== 'undefined') {
      localStorage.setItem("access_token", j.access_token);
    }
  }
  return j;
}

export async function me() {
  const res = await apiFetch("/api/me");
  if (!res.ok) return null;
  return res.json();
}

export async function logout() {
  await apiFetch("/api/auth/logout", { method: "POST" });
  setAccessToken(null);
}
