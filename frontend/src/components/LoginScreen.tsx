"use client";

import { useState } from "react";
import { signIn } from "@/lib/auth-client";

/**
 * Full-screen sign-in gate shown when there's no active session.
 * Phase 2: Google is the only provider.
 */
export default function LoginScreen() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGoogle() {
    setLoading(true);
    setError(null);
    try {
      await signIn.social({ provider: "google", callbackURL: "/" });
      // On success the browser is redirected to Google, so no further code runs.
    } catch {
      setError("Couldn't start sign-in. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#111111] text-white flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-10 h-10 bg-green-400 rounded-lg flex items-center justify-center text-black font-bold">
            H
          </div>
          <div>
            <div className="font-semibold text-white leading-tight text-lg">HookLab</div>
            <div className="text-xs text-gray-500 leading-tight">private practice room</div>
          </div>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-8">
          <h1 className="text-xl font-semibold text-white text-center">Sign in to continue</h1>
          <p className="text-sm text-gray-500 text-center mt-2 mb-6">
            Analyze and sharpen your hooks.
          </p>

          <button
            onClick={handleGoogle}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-white text-gray-800 font-medium rounded-xl px-4 py-3 hover:bg-gray-100 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <GoogleIcon />
            {loading ? "Redirecting…" : "Continue with Google"}
          </button>

          {error && (
            <p className="text-red-400 text-sm text-center mt-4">{error}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
      />
      <path
        fill="#34A853"
        d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"
      />
      <path
        fill="#FBBC05"
        d="M3.964 10.706A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.997 8.997 0 0 0 0 9c0 1.452.348 2.827.957 4.038l3.007-2.332z"
      />
      <path
        fill="#EA4335"
        d="M9 3.583c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.962L3.964 7.294C4.672 5.167 6.656 3.583 9 3.583z"
      />
    </svg>
  );
}
