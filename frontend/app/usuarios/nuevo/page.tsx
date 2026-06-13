"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createUsuario } from "@/lib/api/usuarios";
import { useAuth } from "@/lib/auth/AuthContext";
import {
  canManageUsuarios,
  canViewReportes,
  isAdmin,
} from "@/lib/auth/permissions";
import { SEDE_CENTRAL_ID, SEDE_SECUNDARIA_ID, SEDE_LABELS } from "@/lib/constants";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toaster";

export default function NuevoUsuarioPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nombre, setNombre] = useState("");
  const [idRol, setIdRol] = useState("2");
  const [idSede, setIdSede] = useState(String(user?.id_sede ?? SEDE_CENTRAL_ID));
  const [loading, setLoading] = useState(false);
  const puedeElegirSede = isAdmin(user) || canViewReportes(user);

  if (!canManageUsuarios(user)) {
    return (
      <AppShell title="Nuevo usuario">
        <AccessDenied />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createUsuario({
        email,
        password,
        nombre_completo: nombre,
        id_rol: Number(idRol),
        id_sede: puedeElegirSede ? Number(idSede) : undefined,
      });
      toast("Usuario creado");
      router.push("/usuarios");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Nuevo usuario">
      <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Email</Label>
          <Input className="mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <Label>Contraseña</Label>
          <Input className="mt-1" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        </div>
        <div>
          <Label>Nombre completo</Label>
          <Input className="mt-1" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        </div>
        <div>
          <Label>ID Rol (1=Admin, 2=Analista, 3=DBA)</Label>
          <Input className="mt-1" type="number" value={idRol} onChange={(e) => setIdRol(e.target.value)} />
        </div>
        {puedeElegirSede ? (
          <div>
            <Label>Sede</Label>
            <select
              className="mt-1 w-full rounded-md border border-slate-600 bg-slate-900 px-3 py-2 text-slate-200"
              value={idSede}
              onChange={(e) => setIdSede(e.target.value)}
            >
              <option value={SEDE_CENTRAL_ID}>{SEDE_LABELS[SEDE_CENTRAL_ID]}</option>
              <option value={SEDE_SECUNDARIA_ID}>{SEDE_LABELS[SEDE_SECUNDARIA_ID]}</option>
            </select>
          </div>
        ) : (
          <p className="text-xs text-slate-500">
            El usuario se crea en su sede ({SEDE_LABELS[user?.id_sede ?? SEDE_CENTRAL_ID]}).
          </p>
        )}
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancelar
          </Button>
          <Button type="submit" disabled={loading}>
            Crear
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
