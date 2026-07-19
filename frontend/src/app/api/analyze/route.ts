import { NextResponse, type NextRequest } from "next/server";
import { auth } from "@/lib/auth";

/**
 * BFF proxy for the analyze pipeline.
 *
 * The browser calls this same-origin route (via nextApiClientService) instead of
 * FastAPI directly. Here we:
 *   1. validate the Better Auth session (server-side) — reject if logged out,
 *   2. mint a short-lived JWT for the user,
 *   3. forward the request to FastAPI with the JWT as a Bearer token,
 *   4. relay FastAPI's response back to the browser.
 *
 * The JWT never reaches the browser, and the browser never learns the FastAPI URL.
 */

const FASTAPI_URL = process.env.FASTAPI_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  // 1. Session gate — no session means the request never reaches FastAPI.
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // 2. Mint the JWT FastAPI will verify against /api/auth/jwks.
  const { token } = await auth.api.getToken({ headers: request.headers });

  // 3. Proxy to FastAPI (server-to-server) with the Bearer token.
  const body = await request.text();
  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body,
    });
  } catch {
    return NextResponse.json(
      { error: "Analysis service is unavailable." },
      { status: 502 },
    );
  }

  // 4. Relay the response (status + JSON) back to the browser.
  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}
