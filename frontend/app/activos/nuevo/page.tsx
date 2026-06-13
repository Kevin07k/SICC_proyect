"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createActivo } from "@/lib/api/activos";
import { useAuth } from "@/lib/auth/AuthContext";
import { canManageActivos } from "@/lib/auth/permissions";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toaster";

export default function NuevoActivoPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [hostname, setHostname] = useState("");
  const [ip, setIp] = useState("");
  const [tipo, setTipo] = useState("");
  const [propietario, setPropietario] = useState("");
  const [loading, setLoading] = useState(false);

  if (!canManageActivos(user)) {
    return (
      <AppShell title="Nuevo activo">
        <AccessDenied />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const a = await createActivo({
        hostname,
        direccion_ip: ip || null,
        tipo_activo: tipo || null,
        propietario: propietario || null,
      });
      toast("Activo creado");
      router.push(`/activos/${a.uuid}`);
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Nuevo activo">
      <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Hostname</Label>
          <Input className="mt-1" value={hostname} onChange={(e) => setHostname(e.target.value)} required />
        </div>
        <div>
          <Label>Dirección IP</Label>
          <Input className="mt-1" value={ip} onChange={(e) => setIp(e.target.value)} />
        </div>
        <div>
          <Label>Tipo de activo</Label>
          <Input className="mt-1" value={tipo} onChange={(e) => setTipo(e.target.value)} />
        </div>
        <div>
          <Label>Propietario</Label>
          <Input className="mt-1" value={propietario} onChange={(e) => setPropietario(e.target.value)} />
        </div>
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancelar
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Crear"}
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
