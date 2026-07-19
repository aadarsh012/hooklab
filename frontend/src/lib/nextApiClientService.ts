import type { AnalysisResult } from "@/types/analysis";

/**
 * nextApiClientService — the single seam between the browser UI and the backend.
 *
 * Every backend call the UI makes goes through here. It ONLY ever hits same-origin
 * Next.js API routes (/api/*), never FastAPI directly. The Next.js route handlers
 * are the BFF proxy: they validate the Better Auth session, attach the Bearer JWT
 * server-side, and forward to FastAPI. This keeps the JWT out of client JS and
 * removes browser->FastAPI CORS entirely.
 */

const API_BASE = "/api";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    // Same-origin cookie must ride along so the proxy route can read the session.
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as { detail?: string; error?: string }).detail
      ?? (body as { error?: string }).error
      ?? `Request failed (${res.status})`;
    throw new ApiError(detail, res.status);
  }

  return res.json() as Promise<T>;
}

export const nextApiClientService = {
  analyze(hookText: string): Promise<AnalysisResult> {
    return request<AnalysisResult>("/analyze", {
      method: "POST",
      body: JSON.stringify({ hook_text: hookText }),
    });
  },
};

export { ApiError };
