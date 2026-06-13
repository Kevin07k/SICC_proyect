"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getUsuario, updateUsuario } from "@/lib/api/usuarios";
import { useAuth } from "@/lib/auth/AuthContext";
import { canManageUsuarios } from "@/lib/auth/permissions";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toaster";

export default function EditarUsuarioPage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [nombre, setNombre] = useState("");
  const [idRol, setIdRol] = useState("");
  const [activo, setActivo] = useState(true);
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (!canManageUsuarios(user)) {
      setLoading(false);
      return;
    }
    getUsuario(uuid).then((u) => {
      setEmail(u.email);
      setNombre(u.nombre_completo);
      setIdRol(String(u.id_rol));
      setActivo(u.activo);
      setLoading(false);
    });
  }, [uuid, user]);

  if (!canManageUsuarios(user)) {
    return (
      <AppShell title="Editar usuario">
        <AccessDenied />
      </AppShell>
    );
  }

  if (loading) {
    return (
      <AppShell title="Editar usuario">
        <LoadingState />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateUsuario(uuid, {
        email,
        nombre_completo: nombre,
        id_rol: Number(idRol),
        activo,
        ...(password ? { password } : {}),
      });
      toast("Usuario actualizado");
      router.push("/usuarios");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    }
  };

  return (
    <AppShell title="Editar usuario">
      <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Email</Label>
          <Input className="mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <Label>Nueva contraseña (opcional)</Label>
          <Input className="mt-1" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div>
          <Label>Nombre</Label>
          <Input className="mt-1" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        </div>
        <div>
          <Label>ID Rol</Label>
          <Input className="mt-1" type="number" value={idRol} onChange={(e) => setIdRol(e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" checked={activo} onChange={(e) => setActivo(e.target.checked)} />
          <Label>Activo</Label>
        </div>
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancelar
          </Button>
          <Button type="submit">Guardar</Button>
        </div>
      </form>
    </AppShell>
  );
}
