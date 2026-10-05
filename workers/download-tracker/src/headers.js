/**
 * Public response headers. CORS stays open. HTML also sends a page policy.
 * Author: Aziel Eliab. Identity is Aziel Eliab only.
 */

export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

/** Inline custody page: same-origin fetches, one sigil image, no frames. */
export const PUBLIC_CSP = [
  "default-src 'self'",
  "img-src 'self' https://www.azielcorpuslibrary.net",
  "style-src 'self' 'unsafe-inline'",
  "script-src 'self' 'unsafe-inline'",
  "connect-src 'self'",
  "font-src 'self'",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "object-src 'none'",
].join("; ");

export function htmlHeaders() {
  return {
    "Content-Type": "text/html; charset=utf-8",
    "Content-Security-Policy": PUBLIC_CSP,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    ...corsHeaders(),
  };
}
