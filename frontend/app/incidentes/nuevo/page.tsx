"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createIncidente } from "@/lib/api/incidentes";
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
import { ActivoMultiSelect } from "@/components/incidentes/ActivoMultiSelect";
import type { Estado, Prioridad, TipoIncidente } from "@/types/catalogos";

export default function NuevoIncidentePage() {
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [tipos, setTipos] = useState<TipoIncidente[]>([]);
  const [prioridades, setPrioridades] = useState<Prioridad[]>([]);
  const [estados, setEstados] = useState<Estado[]>([]);
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [idTipo, setIdTipo] = useState("");
  const [idPrioridad, setIdPrioridad] = useState("");
  const [idEstado, setIdEstado] = useState("");
  const [activosSel, setActivosSel] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([listTiposIncidente(), listPrioridades(), listEstados()]).then(
      ([t, p, e]) => {
        setTipos(t.filter((x) => !x.eliminado));
        setPrioridades(p.filter((x) => !x.eliminado));
        setEstados(e.filter((x) => !x.eliminado));
        const nuevo = e.find((x) => x.nombre === "Nuevo");
        if (nuevo) setIdEstado(String(nuevo.id_estado));
        if (t[0]) setIdTipo(String(t[0].id_tipo));
        if (p[0]) setIdPrioridad(String(p[0].id_prioridad));
      },
    );
  }, []);

  if (!canManageIncidentes(user)) {
    return (
      <AppShell title="Nuevo incidente">
        <AccessDenied />
      </AppShell>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const inc = await createIncidente({
        titulo,
        descripcion: descripcion || null,
        id_tipo: Number(idTipo),
        id_prioridad: Number(idPrioridad),
        id_estado: Number(idEstado),
        activos: activosSel,
      });
      toast("Incidente creado");
      router.push(`/incidentes/${inc.uuid}`);
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo crear", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Registrar incidente">
      <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-5">
        <div>
          <Label>Título</Label>
          <Input
            className="mt-1"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            required
            minLength={3}
          />
        </div>
        <div>
          <Label>Descripción</Label>
          <Input
            className="mt-1"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
          />
        </div>
        <div>
          <Label>Tipo</Label>
          <Select value={idTipo} onValueChange={setIdTipo}>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Tipo" />
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
              <SelectValue placeholder="Prioridad" />
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
        <ActivoMultiSelect selected={activosSel} onChange={setActivosSel} />
        <div>
          <Label>Estado</Label>
          <Select value={idEstado} onValueChange={setIdEstado}>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Estado" />
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
        <div className="flex justify-end gap-3 border-t border-slate-700 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancelar
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Crear incidente"}
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
