import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";

/**
 * Better Auth server instance — the identity authority for HookLab.
 *
 * Owns user/session/account/verification/jwks tables in Supabase (Postgres),
 * handles Google OAuth, and issues short-lived JWTs that the FastAPI backend
 * verifies against the /api/auth/jwks endpoint.
 *
 * Env vars are placeholders until Phase 2 (Supabase provisioned + Google
 * credentials created). The config is complete; only the .env values are pending.
 */
export const auth = betterAuth({
  // Base URL is required so Google OAuth redirect URIs resolve correctly.
  baseURL: process.env.BETTER_AUTH_URL,
  secret: process.env.BETTER_AUTH_SECRET,

  // Supabase Postgres connection. Better Auth uses the pg Pool via Kysely
  // and manages its own schema (run the Better Auth CLI migration in Phase 2).
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    },
  },

  // jwt(): exposes /api/auth/token (issue JWT) and /api/auth/jwks (public keys)
  //        so the Python backend can verify tokens statelessly.
  // nextCookies(): must be last — handles cookie setting in Next.js server actions.
  plugins: [jwt(), nextCookies()],
});
