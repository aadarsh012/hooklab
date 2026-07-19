import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

/**
 * Catch-all Better Auth route handler.
 *
 * Serves every Better Auth endpoint under /api/auth/* — OAuth callbacks,
 * session, sign-out, /api/auth/token (JWT), and /api/auth/jwks (public keys).
 */
export const { GET, POST } = toNextJsHandler(auth);
