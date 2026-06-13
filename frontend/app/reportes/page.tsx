"use client";

import { useState } from "react";
import { BarChart3, Database, Play, RefreshCw } from "lucide-react";
import { getReporteGlobal, regenerarReporteGlobal } from "@/lib/api/reportes";
import { useAuthGate } from "@/hooks/useAuthGate";
import { canViewReportes } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils";
import { AppShell } from "@/components/layout/AppShell";
import { ReportesGlobalesPanel } from "@/components/reportes/ReportesGlobalesPanel";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api/client";
import { useToast } from "@/components/ui/toaster";
import type { ReporteGlobalResponse } from "@/types/reportes";

export default function ReportesPage() {
  const { status } = useAuthGate(canViewReportes);
  const { toast } = useToast();
  const [data, setData] = useState<ReporteGlobalResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  const handleConsultar = async () => {
    setLoading(true);
    try {
      const res = await getReporteGlobal(false);
      setData(res);
      toast(
        res.from_cache ? "Reporte cargado" : "Reporte generado",
        res.from_cache
          ? "Datos desde caché central (vigentes hasta la fecha indicada)."
          : "Consolidación calculada ahora.",
      );
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo cargar", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerar = async () => {
    setRegenerating(true);
    try {
      const res = await regenerarReporteGlobal();
      setData(res);
      toast("Reporte regenerado", "Vista global actualizada desde ambas sedes.");
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo regenerar", "error");
    } finally {
      setRegenerating(false);
    }
  };

  if (status === "loading") {
    return (
      <AppShell title="Reportes globales">
        <LoadingState />
      </AppShell>
    );
  }

  if (status === "denied") {
    return (
      <AppShell title="Reportes globales">
        <AccessDenied message="Reportes globales solo para sede central con permiso reportes.ver." />
      </AppShell>
    );
  }

  const busy = loading || regenerating;

  return (
    <AppShell
      title="Reportes globales"
      actions={
        data ? (
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={data.from_cache ? "muted" : "success"}>
              {data.from_cache ? "Desde caché" : "Recién calculado"}
            </Badge>
            <span className="text-xs text-slate-500">
              TTL {data.ttl_seconds}s
              {data.duration_ms != null && ` · ${data.duration_ms} ms`}
            </span>
          </div>
        ) : undefined
      }
    >
      <p className="mb-6 flex items-start gap-2 text-sm text-slate-400">
        <Database className="mt-0.5 h-4 w-4 shrink-0 text-cyan-500" />
        Consolidación de Santa Cruz (PostgreSQL) y Cochabamba (MySQL). El reporte{" "}
        <strong className="text-slate-300">no se carga solo</strong>: use los botones cuando quiera
        ver o actualizar la vista global.
      </p>

      <div className="mb-8 flex flex-wrap gap-3">
        <Button disabled={busy} onClick={() => void handleConsultar()}>
          <Play className="h-4 w-4" />
          {loading ? "Consultando..." : "Consultar reporte"}
        </Button>
        <Button variant="secondary" disabled={busy} onClick={() => void handleRegenerar()}>
          <RefreshCw className={`h-4 w-4 ${regenerating ? "animate-spin" : ""}`} />
          {regenerating ? "Regenerando..." : "Regenerar desde sedes"}
        </Button>
      </div>

      <p className="mb-6 text-xs text-slate-500">
        <strong>Consultar:</strong> usa la caché en central si aún es válida (más rápido).{" "}
        <strong>Regenerar:</strong> vuelve a leer ambas BDs y guarda un reporte nuevo (puede tardar
        varios segundos).
      </p>

      {data && (
        <p className="mb-6 text-xs text-slate-500">
          Generado: {formatDate(data.generated_at)} · Válido hasta: {formatDate(data.expires_at)}
        </p>
      )}

      {loading || regenerating ? (
        <LoadingState
          label={
            regenerating
              ? "Regenerando reporte global desde ambas sedes..."
              : "Consultando reporte global..."
          }
        />
      ) : data ? (
        <ReportesGlobalesPanel payload={data.payload} />
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/30 py-16 text-center">
          <BarChart3 className="mb-4 h-12 w-12 text-slate-600" />
          <p className="text-slate-400">Aún no hay reporte cargado en pantalla.</p>
          <p className="mt-2 max-w-md text-sm text-slate-500">
            Pulse &quot;Consultar reporte&quot; para mostrar la última vista disponible, o
            &quot;Regenerar desde sedes&quot; si necesita datos recién calculados.
          </p>
        </div>
      )}
    </AppShell>
  );
}
