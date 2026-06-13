"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getIncidente, updateIncidente } from "@/lib/api/incidentes";
import { listBitacora, createBitacora } from "@/lib/api/bitacora";
import { useAuth } from "@/lib/auth/AuthContext";
import {
  canManageIncidentes,
  canManageDocumentosIncidente,
  canViewBitacora,
  canViewIncidentes,
} from "@/lib/auth/permissions";
import { usePaginatedTable } from "@/hooks/usePaginatedTable";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";
import { AppShell } from "@/components/layout/AppShell";
import { PaginationControls } from "@/components/shared/PaginationControls";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Badge, priorityVariant } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/toaster";
import { ActivosVinculadosSection } from "@/components/incidentes/ActivosVinculadosSection";
import { IncidenteDocumentosPanel } from "@/components/mongo/IncidenteDocumentosPanel";
import type { Incidente } from "@/types/incidentes";
import type { BitacoraEntry } from "@/types/bitacora";

export default function IncidenteDetallePage() {
  const params = useParams();
  const uuid = params.uuid as string;
  const { user } = useAuth();
  const { toast } = useToast();
  const [incidente, setIncidente] = useState<Incidente | null>(null);
  const [bitacora, setBitacora] = useState<BitacoraEntry[]>([]);
  const [comentario, setComentario] = useState("");
  const [loading, setLoading] = useState(true);

  const table = usePaginatedTable(bitacora, {
    pageSize: 5,
    searchKeys: ["comentario", "usuario_nombre"],
  });

  const load = () => {
    Promise.all([
      getIncidente(uuid),
      canViewBitacora(user) ? listBitacora(uuid) : Promise.resolve([]),
    ])
      .then(([inc, bit]) => {
        setIncidente(inc);
        setBitacora(bit);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!canViewIncidentes(user)) {
      setLoading(false);
      return;
    }
    load();
  }, [uuid, user]);

  const handleComentario = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comentario.trim()) return;
    try {
      await createBitacora(uuid, { comentario });
      setComentario("");
      const bit = await listBitacora(uuid);
      setBitacora(bit);
      toast("Comentario añadido");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    }
  };

  const handleCerrar = async () => {
    try {
      await updateIncidente(uuid, {
        fecha_cierre: new Date().toISOString(),
      });
      toast("Incidente cerrado");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    }
  };

  const backButton = (
    <Button variant="secondary" asChild>
      <Link href="/incidentes">
        <ArrowLeft className="h-4 w-4" />
        Volver
      </Link>
    </Button>
  );

  if (!canViewIncidentes(user)) {
    return (
      <AppShell title="Incidente" actions={backButton}>
        <AccessDenied />
      </AppShell>
    );
  }

  if (loading) {
    return (
      <AppShell title="Incidente" actions={backButton}>
        <LoadingState />
      </AppShell>
    );
  }

  if (!incidente) {
    return (
      <AppShell title="Incidente" actions={backButton}>
        <p className="text-slate-400">No encontrado</p>
      </AppShell>
    );
  }

  return (
    <AppShell
      title={incidente.titulo}
      actions={
        <>
          {backButton}
          {canManageIncidentes(user) && (
            <>
              <Button variant="outline" asChild>
                <Link href={`/incidentes/${uuid}/editar`}>Editar</Link>
              </Button>
              {!incidente.fecha_cierre && (
                <Button variant="secondary" onClick={handleCerrar}>
                  Cerrar incidente
                </Button>
              )}
            </>
          )}
        </>
      }
    >
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <ActivosVinculadosSection
            incidenteUuid={uuid}
            initialVinculos={incidente.activos_vinculados ?? []}
            canManage={canManageIncidentes(user)}
          />
          {canViewBitacora(user) && (
            <>
              <h3 className="text-lg font-semibold text-slate-200">Bitácora</h3>
              {canManageIncidentes(user) && (
                <form onSubmit={handleComentario} className="flex gap-2">
                  <Input
                    placeholder="Nuevo comentario..."
                    value={comentario}
                    onChange={(e) => setComentario(e.target.value)}
                    className="flex-1"
                  />
                  <Button type="submit">Añadir</Button>
                </form>
              )}
              <div className="space-y-3">
                {table.paginated.map((b) => (
                  <div
                    key={b.uuid}
                    className="rounded-lg border border-slate-700 bg-slate-800/40 p-4"
                  >
                    <p className="text-sm text-slate-300">{b.comentario}</p>
                    <p className="mt-2 text-xs text-slate-500">
                      {b.usuario_nombre ?? "Usuario"} · {formatDate(b.created_at)}
                    </p>
                  </div>
                ))}
              </div>
              <PaginationControls
                page={table.page}
                totalPages={table.totalPages}
                rangeStart={table.rangeStart}
                rangeEnd={table.rangeEnd}
                total={table.total}
                onPageChange={table.setPage}
              />
            </>
          )}
          <IncidenteDocumentosPanel
            incidenteUuid={uuid}
            canManage={canManageDocumentosIncidente(user)}
          />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Datos del caso</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <span className="text-slate-500">Estado:</span> {incidente.estado_nombre}
            </p>
            <p>
              <span className="text-slate-500">Prioridad:</span>{" "}
              <Badge variant={priorityVariant(incidente.prioridad_nivel)}>
                {incidente.prioridad_nivel}
              </Badge>
            </p>
            <p>
              <span className="text-slate-500">Tipo:</span> {incidente.tipo_nombre}
            </p>
            <p>
              <span className="text-slate-500">Descripción:</span>{" "}
              {incidente.descripcion ?? "—"}
            </p>
            <p>
              <span className="text-slate-500">Cierre:</span>{" "}
              {formatDate(incidente.fecha_cierre)}
            </p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
