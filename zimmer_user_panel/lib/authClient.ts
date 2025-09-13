let _accessToken: string | null = null;

export function setAccessToken(tok: string | null) {
  _accessToken = tok;
}
export function getAccessToken(): string | null {
  return _accessToken;
}
export function isAuthenticated(): boolean {
  return !!_accessToken;
}
