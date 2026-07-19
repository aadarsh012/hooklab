import { createAuthClient } from "better-auth/react";

/**
 * Better Auth client for use in React components.
 *
 * Exposes signIn / signOut / useSession. In Phase 2 the login UI will call
 * authClient.signIn.social({ provider: "google" }).
 *
 * baseURL is omitted intentionally — the client defaults to the same origin,
 * which is correct since Better Auth is served from this Next.js app.
 */
export const authClient = createAuthClient();

export const { signIn, signOut, useSession } = authClient;
