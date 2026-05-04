const DEFAULT_BACKEND_URL = "https://aica-sys.onrender.com";

const DEPRECATED_BACKEND_HOSTS = new Set(["aica-sys-backend.onrender.com"]);

function withDefaultProtocol(url: string): string {
  if (/^https?:\/\//.test(url)) {
    return url;
  }
  return `https://${url}`;
}

export function resolveBackendUrl(): string {
  const raw = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || DEFAULT_BACKEND_URL;

  try {
    const parsed = new URL(withDefaultProtocol(raw));
    if (DEPRECATED_BACKEND_HOSTS.has(parsed.hostname)) {
      return DEFAULT_BACKEND_URL;
    }
    return parsed.origin;
  } catch {
    return DEFAULT_BACKEND_URL;
  }
}
