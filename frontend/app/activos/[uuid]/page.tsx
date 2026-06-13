"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getActivo, updateActivo } from "@/lib/api/activos";
import { useAuth } from "@/lib/auth/AuthContext";
import { canManageActivos, canManageDocumentosActivo, canViewActivos } from "@/lib/auth/permissions";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toaster";
import { ActivoTelemetriaPanel } from "@/components/mongo/ActivoTelemetriaPanel";

export default function EditarActivoPage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hostname, setHostname] = useState("");
  const [ip, setIp] = useState("");
  const [tipo, setTipo] = useState("");
  const [propietario, setPropietario] = useState("");
  const [eliminado, setEliminado] = useState(false);

  const canEdit = canManageActivos(user);
  const canTelemetria = canManageDocumentosActivo(user);

  useEffect(() => {
    if (!canViewActivos(user)) {
      setLoading(false);
      return;
    }
    getActivo(uuid).then((a) => {
      setHostname(a.hostname);
      setIp(a.direccion_ip ?? "");
      setTipo(a.tipo_activo ?? "");
      setPropietario(a.propietario ?? "");
      setEliminado(a.eliminado);
      setLoading(false);
    });
  }, [uuid, user]);

  if (!canViewActivos(user)) {
    return (
      <AppShell title="Activo">
        <AccessDenied />
      </AppShell>
    );
  }

  if (loading) {
    return (
      <AppShell title="Editar activo">
        <LoadingState />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateActivo(uuid, {
        hostname,
        direccion_ip: ip || null,
        tipo_activo: tipo || null,
        propietario: propietario || null,
        eliminado,
      });
      toast("Activo actualizado");
      router.push("/activos");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell title={canEdit ? "Editar activo" : "Detalle activo"}>
      <form onSubmit={canEdit ? handleSubmit : (e) => e.preventDefault()} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Hostname</Label>
          <Input className="mt-1" value={hostname} onChange={(e) => setHostname(e.target.value)} required readOnly={!canEdit} />
        </div>
        <div>
          <Label>Dirección IP</Label>
          <Input className="mt-1" value={ip} onChange={(e) => setIp(e.target.value)} readOnly={!canEdit} />
        </div>
        <div>
          <Label>Tipo</Label>
          <Input className="mt-1" value={tipo} onChange={(e) => setTipo(e.target.value)} readOnly={!canEdit} />
        </div>
        <div>
          <Label>Propietario</Label>
          <Input className="mt-1" value={propietario} onChange={(e) => setPropietario(e.target.value)} readOnly={!canEdit} />
        </div>
        {canEdit && (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="eliminado"
              checked={eliminado}
              onChange={(e) => setEliminado(e.target.checked)}
              className="rounded border-slate-600"
            />
            <Label htmlFor="eliminado">Baja lógica (eliminado)</Label>
          </div>
        )}
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Volver
          </Button>
          {canEdit && (
            <Button type="submit" disabled={saving}>
              {saving ? "Guardando..." : "Guardar"}
            </Button>
          )}
        </div>
      </form>
      <ActivoTelemetriaPanel activoUuid={uuid} canManage={canTelemetria} />
    </AppShell>
  );
}
