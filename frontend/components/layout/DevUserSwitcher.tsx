"use client";

import { useState } from "react";
import { FlaskConical } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { DEV_SWITCHER_ENABLED, TEST_USERS } from "@/lib/dev/test-users";
import { SEDE_LABELS } from "@/lib/constants";
import { useToast } from "@/components/ui/toaster";

export function DevUserSwitcher() {
  const { user, switchUser } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  if (!DEV_SWITCHER_ENABLED || !user) return null;

  const handleChange = async (uuid: string) => {
    if (uuid === user.uuid) return;
    setLoading(true);
    try {
      await switchUser(uuid);
      toast("Usuario cambiado", "Sesión de prueba actualizada");
    } catch (e) {
      toast("Error", e instanceof Error ? e.message : "No se pudo cambiar", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4 rounded-lg border border-amber-600/40 bg-amber-950/30 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-amber-400">
        <FlaskConical className="h-3.5 w-3.5" />
        Modo prueba
      </div>
      <p className="mb-2 text-xs text-slate-400">
        Sede: {SEDE_LABELS[user.id_sede] ?? user.id_sede} · {user.rol_nombre}
      </p>
      <select
        className="w-full rounded-md border border-slate-600 bg-slate-900 px-2 py-1.5 text-xs text-slate-200"
        value={user.uuid}
        disabled={loading}
        onChange={(e) => handleChange(e.target.value)}
      >
        {TEST_USERS.map((u) => (
          <option key={u.uuid} value={u.uuid}>
            {u.nombre} ({u.sede})
          </option>
        ))}
      </select>
    </div>
  );
}
