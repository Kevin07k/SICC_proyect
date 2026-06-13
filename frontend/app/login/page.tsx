"use client";

import { useState } from "react";
import Link from "next/link";
import { Shield } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { DEV_SWITCHER_ENABLED } from "@/lib/dev/test-users";
import { DevQuickLogin } from "@/components/auth/DevQuickLogin";
import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@sicc.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-gradient relative flex min-h-screen items-center justify-center p-4">
      <div className="glass-card w-full max-w-md rounded-2xl p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <Shield className="mx-auto mb-4 h-14 w-14 text-blue-500 animate-pulse-glow" />
          <h1 className="text-2xl font-bold text-slate-100">SICC</h1>
          <p className="mt-1 text-sm text-slate-400">
            Sistema Integrado de Ciberseguridad y Control
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <Label htmlFor="email">Correo</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1.5"
            />
          </div>
          <div>
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1.5"
            />
          </div>
          {error && (
            <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {error}
            </p>
          )}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Entrando..." : "Iniciar sesión"}
          </Button>
        </form>
        {DEV_SWITCHER_ENABLED && (
          <>
            <DevQuickLogin />
            <p className="mt-3 text-center text-sm text-slate-500">
              <Link href="/dev/switch" className="text-cyan-400 hover:underline">
                Panel de prueba completo
              </Link>
            </p>
          </>
        )}
        <p className="mt-4 text-center text-xs text-slate-600">
          Demo: admin@sicc.com / admin123 o test123 en usuarios test
        </p>
      </div>
    </div>
  );
}
