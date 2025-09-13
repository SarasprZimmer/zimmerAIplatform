export function rial(n: number) {
  try { return n.toLocaleString("fa-IR"); } catch { return String(n); }
}