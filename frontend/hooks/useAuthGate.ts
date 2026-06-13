"use client";

import { useAuth } from "@/lib/auth/AuthContext";
import type { CurrentUser } from "@/types/auth";

type AuthGateStatus = "loading" | "denied" | "ready";

export function useAuthGate(
  check: (user: CurrentUser | null) => boolean,
): { status: AuthGateStatus; user: CurrentUser | null } {
  const { user, loading } = useAuth();

  if (loading) return { status: "loading", user: null };
  if (!user || !check(user)) return { status: "denied", user };
  return { status: "ready", user };
}
