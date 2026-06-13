"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { getMe, login as apiLogin } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { clearUuidCookie, getUuidFromDocument, setUuidCookie } from "@/lib/auth/cookie";
import { hasPermiso, isAdmin } from "@/lib/auth/permissions";
import type { CurrentUser, LoginRequest } from "@/types/auth";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  error: string | null;
  login: (body: LoginRequest) => Promise<void>;
  logout: () => void;
  switchUser: (uuid: string) => Promise<void>;
  refresh: () => Promise<void>;
  hasPermiso: (codigo: string) => boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const uuid = getUuidFromDocument();
    if (!uuid) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await getMe(uuid);
      setUser(me);
      setError(null);
    } catch (e) {
      setUser(null);
      if (e instanceof ApiError && e.status === 401) clearUuidCookie();
      setError(e instanceof Error ? e.message : "Error de sesión");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = useCallback(
    async (body: LoginRequest) => {
      const res = await apiLogin(body);
      setUuidCookie(res.uuid);
      setUser(res);
      setError(null);
      router.push("/");
    },
    [router],
  );

  const logout = useCallback(() => {
    clearUuidCookie();
    setUser(null);
    router.push("/login");
  }, [router]);

  const switchUser = useCallback(
    async (uuid: string) => {
      setUuidCookie(uuid);
      setLoading(true);
      try {
        const me = await getMe(uuid);
        setUser(me);
        setError(null);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Error al cambiar usuario");
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [router],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      error,
      login,
      logout,
      switchUser,
      refresh,
      hasPermiso: (codigo) => hasPermiso(user, codigo),
      isAdmin: isAdmin(user),
    }),
    [user, loading, error, login, logout, switchUser, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
