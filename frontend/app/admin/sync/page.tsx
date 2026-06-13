"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { getSyncStatus, runSyncManual } from "@/lib/api/sync";
import { useAuth } from "@/lib/auth/AuthContext";
import { canSync } from "@/lib/auth/permissions";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";
import { AppShell } from "@/components/layout/AppShell";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/components/ui/toaster";
import type { SyncStatusResponse } from "@/types/sync";

export default function SyncAdminPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [status, setStatus] = useState<SyncStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const load = () => {
    getSyncStatus()
      .then(setStatus)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!canSync(user)) {
      setLoading(false);
      return;
    }
    load();
  }, [user]);

  const handleSync = async () => {
    setRunning(true);
    try {
      const res = await runSyncManual();
      toast(
        "Sync completado",
        `${res.registros_aplicados} registros en ${res.tablas_procesadas.length} tablas`,
      );
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setRunning(false);
    }
  };

  if (!canSync(user)) {
    return (
      <AppShell title="Sincronización">
        <AccessDenied message="Se requiere permiso sync.ejecutar o rol Administrador." />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Sincronización LWW"
      actions={
        <Button onClick={handleSync} disabled={running}>
          <RefreshCw className={`h-4 w-4 ${running ? "animate-spin" : ""}`} />
          {running ? "Sincronizando..." : "Ejecutar sync manual"}
        </Button>
      }
    >
      {loading ? (
        <LoadingState />
      ) : status ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
              <p className="text-xs text-slate-500">PostgreSQL</p>
              <p className="text-sm text-slate-200">{formatDate(status.last_sync_postgres)}</p>
            </div>
            <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
              <p className="text-xs text-slate-500">MySQL</p>
              <p className="text-sm text-slate-200">{formatDate(status.last_sync_mysql)}</p>
            </div>
            <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
              <p className="text-xs text-slate-500">Efectiva</p>
              <p className="text-sm text-slate-200">{formatDate(status.effective_last_sync)}</p>
            </div>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tabla</TableHead>
                <TableHead>Pendientes PG</TableHead>
                <TableHead>Pendientes MySQL</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {status.tablas.map((t) => (
                <TableRow key={t.tabla}>
                  <TableCell>{t.tabla}</TableCell>
                  <TableCell>{t.pendientes_postgres}</TableCell>
                  <TableCell>{t.pendientes_mysql}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <p className="text-slate-400">Sin datos de estado</p>
      )}
    </AppShell>
  );
}
