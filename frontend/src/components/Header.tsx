"use client";

import { useState } from "react";
import { useSession, signOut } from "@/lib/auth-client";

export default function Header() {
  const { data: session } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);
  const user = session?.user;

  const initials = (user?.name ?? user?.email ?? "You")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-[#2a2a2a]">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-green-400 rounded-lg flex items-center justify-center text-black font-bold text-sm">
          H
        </div>
        <div>
          <div className="font-semibold text-white leading-tight">HookLab</div>
          <div className="text-xs text-gray-500 leading-tight">private practice room</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="px-4 py-1.5 border border-[#3a3a3a] rounded-lg text-sm text-gray-300 hover:border-gray-500 hover:text-white transition-colors">
          Library
        </button>

        <div className="relative">
          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="flex items-center gap-2 focus:outline-none"
            aria-label="Account menu"
          >
            {user?.image ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={user.image}
                alt={user.name ?? "You"}
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white text-[10px] font-semibold">
                {initials}
              </div>
            )}
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl shadow-lg py-2 z-50">
              <div className="px-4 py-2 border-b border-[#2a2a2a]">
                <div className="text-sm text-white truncate">{user?.name ?? "You"}</div>
                {user?.email && (
                  <div className="text-xs text-gray-500 truncate">{user.email}</div>
                )}
              </div>
              <button
                onClick={() => signOut()}
                className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#222] hover:text-white transition-colors"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
