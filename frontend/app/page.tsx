"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Server, RefreshCw } from "lucide-react";
import { listIncidentes } from "@/lib/api/incidentes";
import { listActivos } from "@/lib/api/activos";
import { getSyncStatus } from "@/lib/api/sync";
import { useAuth } from "@/lib/auth/AuthContext";
import { canSync, canViewActivos, canViewIncidentes } from "@/lib/auth/permissions";
import { CLOSED_STATES, SEDE_LABELS } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardCharts } from "@/components/dashboard/DashboardCharts";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Incidente } from "@/types/incidentes";
import type { Activo } from "@/types/activos";
import type { SyncStatusResponse } from "@/types/sync";

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [incidentes, setIncidentes] = useState<Incidente[]>([]);
  const [activos, setActivos] = useState<Activo[]>([]);
  const [syncStatus, setSyncStatus] = useState<SyncStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;
    const tasks: Promise<void>[] = [];
    if (canViewIncidentes(user)) {
      tasks.push(listIncidentes().then(setIncidentes));
    }
    if (canViewActivos(user)) {
      tasks.push(listActivos().then(setActivos));
    }
    if (canSync(user)) {
      tasks.push(getSyncStatus().then(setSyncStatus).catch(() => setSyncStatus(null)));
    }
    Promise.all(tasks).finally(() => setLoading(false));
  }, [user, authLoading]);

  if (authLoading) return <LoadingState />;
  if (!user) return null;

  const abiertos = incidentes.filter(
    (i) => !i.eliminado && i.estado_nombre && !CLOSED_STATES.includes(i.estado_nombre),
  );
  const criticos = abiertos.filter((i) => {
    const p = (i.prioridad_nivel ?? "").toLowerCase();
    return p.includes("crit") || p.includes("alta");
  });
  const activosCount = activos.filter((a) => !a.eliminado).length;

  return (
    <AppShell
      title="Dashboard"
      actions={
        user && (
          <span className="rounded-lg bg-blue-950/50 px-3 py-1 text-sm text-blue-300">
            {SEDE_LABELS[user.id_sede] ?? `Sede ${user.id_sede}`}
          </span>
        )
      }
    >
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Incidentes abiertos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-slate-100">{abiertos.length}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Críticos / Alta
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-orange-400">{criticos.length}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Activos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-purple-400">{activosCount}</p>
              </CardContent>
            </Card>
            {syncStatus && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-400">
                    Última sync
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-200">
                    {formatDate(syncStatus.effective_last_sync)}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {canViewIncidentes(user) ? (
            <DashboardCharts incidentes={incidentes} activos={activos} />
          ) : (
            <AccessDenied message="Sin permiso para ver métricas de incidentes." />
          )}

          <div className="mt-8 flex flex-wrap gap-3">
            {canViewIncidentes(user) && (
              <Button asChild>
                <Link href="/incidentes">
                  <AlertTriangle className="h-4 w-4" />
                  Ver incidentes
                </Link>
              </Button>
            )}
            {canViewActivos(user) && (
              <Button asChild variant="secondary">
                <Link href="/activos">
                  <Server className="h-4 w-4" />
                  Ver activos
                </Link>
              </Button>
            )}
            {canSync(user) && (
              <Button asChild variant="outline">
                <Link href="/admin/sync">
                  <RefreshCw className="h-4 w-4" />
                  Sincronización
                </Link>
              </Button>
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}
