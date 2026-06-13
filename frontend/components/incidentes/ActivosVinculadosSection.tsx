"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listActivos } from "@/lib/api/activos";
import {
  linkActivoIncidente,
  listActivosIncidente,
  unlinkActivoIncidente,
} from "@/lib/api/incidentes";
import { ApiError } from "@/lib/api/client";
import { useToast } from "@/components/ui/toaster";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Activo } from "@/types/activos";
import type { IncidenteActivoVinculo } from "@/types/incidentes";

type Props = {
  incidenteUuid: string;
  initialVinculos?: IncidenteActivoVinculo[];
  canManage: boolean;
  onChange?: (vinculos: IncidenteActivoVinculo[]) => void;
};

export function ActivosVinculadosSection({
  incidenteUuid,
  initialVinculos = [],
  canManage,
  onChange,
}: Props) {
  const { toast } = useToast();
  const [vinculos, setVinculos] = useState<IncidenteActivoVinculo[]>(initialVinculos);
  const [activos, setActivos] = useState<Activo[]>([]);
  const [selectedActivo, setSelectedActivo] = useState("");
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    const list = await listActivosIncidente(incidenteUuid);
    setVinculos(list);
    onChange?.(list);
  };

  useEffect(() => {
    setVinculos(initialVinculos);
  }, [initialVinculos]);

  useEffect(() => {
    if (canManage) {
      listActivos().then(setActivos).catch(() => setActivos([]));
    }
  }, [canManage]);

  const linkedIds = new Set(vinculos.map((v) => v.id_activo));
  const disponibles = activos.filter((a) => !linkedIds.has(a.uuid));

  const handleLink = async () => {
    if (!selectedActivo) return;
    setLoading(true);
    try {
      await linkActivoIncidente(incidenteUuid, { id_activo: selectedActivo });
      setSelectedActivo("");
      await refresh();
      toast("Activo vinculado");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo vincular", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleUnlink = async (vinculoUuid: string) => {
    setLoading(true);
    try {
      await unlinkActivoIncidente(incidenteUuid, vinculoUuid);
      await refresh();
      toast("Vínculo eliminado");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-200">Activos afectados</h3>
      {vinculos.length === 0 ? (
        <p className="text-sm text-slate-500">Sin activos vinculados</p>
      ) : (
        <ul className="space-y-3">
          {vinculos.map((v) => (
            <li
              key={v.uuid}
              className="rounded-lg border border-slate-700 bg-slate-800/40 p-4 text-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-slate-200">
                    {v.hostname_registrado ?? v.hostname_actual ?? "Activo"}
                    {v.activo_eliminado && (
                      <span className="ml-2 text-xs text-slate-500">(baja / traslado)</span>
                    )}
                  </p>
                  <p className="mt-1 text-slate-400">
                    Tipo registrado: {v.tipo_activo_registrado ?? "—"}
                  </p>
                  <p className="text-slate-400">Sede registrada: {v.sede_registrada ?? "—"}</p>
                  {!v.activo_eliminado && v.hostname_actual && (
                    <Link
                      href={`/activos/${v.id_activo}`}
                      className="mt-2 inline-block text-xs text-blue-400 hover:underline"
                    >
                      Ver activo actual
                    </Link>
                  )}
                </div>
                {canManage && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    disabled={loading}
                    onClick={() => handleUnlink(v.uuid)}
                  >
                    Quitar
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {canManage && (
        <div className="flex flex-wrap items-end gap-2 border-t border-slate-700 pt-4">
          <div className="min-w-[200px] flex-1">
            <Label>Añadir activo de la sede</Label>
            <Select value={selectedActivo} onValueChange={setSelectedActivo}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Seleccionar activo" />
              </SelectTrigger>
              <SelectContent>
                {disponibles.map((a) => (
                  <SelectItem key={a.uuid} value={a.uuid}>
                    {a.hostname}
                    {a.tipo_activo ? ` (${a.tipo_activo})` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            type="button"
            disabled={loading || !selectedActivo}
            onClick={handleLink}
          >
            Vincular
          </Button>
        </div>
      )}
    </div>
  );
}
