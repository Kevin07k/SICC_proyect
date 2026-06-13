"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getIncidente, updateIncidente } from "@/lib/api/incidentes";
import {
  listEstados,
  listPrioridades,
  listTiposIncidente,
} from "@/lib/api/catalogos";
import { useAuth } from "@/lib/auth/AuthContext";
import { canManageIncidentes } from "@/lib/auth/permissions";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/toaster";
import { ActivosVinculadosSection } from "@/components/incidentes/ActivosVinculadosSection";
import type { IncidenteActivoVinculo } from "@/types/incidentes";

export default function EditarIncidentePage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [idTipo, setIdTipo] = useState("");
  const [idPrioridad, setIdPrioridad] = useState("");
  const [idEstado, setIdEstado] = useState("");
  const [tipos, setTipos] = useState<{ id_tipo: number; nombre: string }[]>([]);
  const [prioridades, setPrioridades] = useState<{ id_prioridad: number; nivel: string }[]>([]);
  const [estados, setEstados] = useState<{ id_estado: number; nombre: string }[]>([]);
  const [activosVinculados, setActivosVinculados] = useState<IncidenteActivoVinculo[]>([]);

  useEffect(() => {
    if (!canManageIncidentes(user)) {
      setLoading(false);
      return;
    }
    Promise.all([
      getIncidente(uuid),
      listTiposIncidente(),
      listPrioridades(),
      listEstados(),
    ]).then(([inc, t, p, e]) => {
      setTitulo(inc.titulo);
      setDescripcion(inc.descripcion ?? "");
      setIdTipo(String(inc.id_tipo));
      setIdPrioridad(String(inc.id_prioridad));
      setIdEstado(String(inc.id_estado));
      setTipos(t);
      setPrioridades(p);
      setEstados(e);
      setActivosVinculados(inc.activos_vinculados ?? []);
      setLoading(false);
    });
  }, [uuid, user]);

  if (!canManageIncidentes(user)) {
    return (
      <AppShell title="Editar incidente">
        <AccessDenied />
      </AppShell>
    );
  }

  if (loading) {
    return (
      <AppShell title="Editar incidente">
        <LoadingState />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateIncidente(uuid, {
        titulo,
        descripcion: descripcion || null,
        id_tipo: Number(idTipo),
        id_prioridad: Number(idPrioridad),
        id_estado: Number(idEstado),
      });
      toast("Incidente actualizado");
      router.push(`/incidentes/${uuid}`);
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell title="Editar incidente">
      <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Título</Label>
          <Input className="mt-1" value={titulo} onChange={(e) => setTitulo(e.target.value)} required />
        </div>
        <div>
          <Label>Descripción</Label>
          <Input className="mt-1" value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
        </div>
        <div>
          <Label>Tipo</Label>
          <Select value={idTipo} onValueChange={setIdTipo}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {tipos.map((t) => (
                <SelectItem key={t.id_tipo} value={String(t.id_tipo)}>
                  {t.nombre}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Prioridad</Label>
          <Select value={idPrioridad} onValueChange={setIdPrioridad}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {prioridades.map((p) => (
                <SelectItem key={p.id_prioridad} value={String(p.id_prioridad)}>
                  {p.nivel}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Estado</Label>
          <Select value={idEstado} onValueChange={setIdEstado}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {estados.map((e) => (
                <SelectItem key={e.id_estado} value={String(e.id_estado)}>
                  {e.nombre}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <ActivosVinculadosSection
          incidenteUuid={uuid}
          initialVinculos={activosVinculados}
          canManage
          onChange={setActivosVinculados}
        />
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancelar
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? "Guardando..." : "Guardar"}
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
