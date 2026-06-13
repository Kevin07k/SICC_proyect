"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import { listIncidentes } from "@/lib/api/incidentes";
import { useAuthGate } from "@/hooks/useAuthGate";
import { canManageIncidentes, canViewIncidentes } from "@/lib/auth/permissions";
import { usePaginatedTable } from "@/hooks/usePaginatedTable";
import { formatDate } from "@/lib/utils";
import { AppShell } from "@/components/layout/AppShell";
import { SearchBar } from "@/components/shared/SearchBar";
import { PaginationControls } from "@/components/shared/PaginationControls";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Badge, priorityVariant } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Incidente } from "@/types/incidentes";

export default function IncidentesPage() {
  const { status, user } = useAuthGate(canViewIncidentes);
  const [rows, setRows] = useState<Incidente[]>([]);
  const [loading, setLoading] = useState(true);

  const table = usePaginatedTable(rows, {
    pageSize: 10,
    searchKeys: ["titulo", "estado_nombre", "prioridad_nivel", "tipo_nombre"],
  });

  useEffect(() => {
    if (status !== "ready") {
      setLoading(false);
      return;
    }
    listIncidentes()
      .then(setRows)
      .finally(() => setLoading(false));
  }, [status]);

  if (status === "loading") {
    return (
      <AppShell title="Incidentes">
        <LoadingState />
      </AppShell>
    );
  }

  if (status === "denied") {
    return (
      <AppShell title="Incidentes">
        <AccessDenied />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Incidentes"
      actions={
        canManageIncidentes(user) && (
          <Button asChild>
            <Link href="/incidentes/nuevo">
              <Plus className="h-4 w-4" />
              Registrar
            </Link>
          </Button>
        )
      }
    >
      <div className="mb-6">
        <SearchBar
          value={table.search}
          onChange={table.setSearch}
          placeholder="Buscar por título, estado, prioridad..."
        />
      </div>
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Título</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Prioridad</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Actualizado</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.paginated.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-slate-500">
                    Sin incidentes
                  </TableCell>
                </TableRow>
              ) : (
                table.paginated.map((inc) => (
                  <TableRow key={inc.uuid} className={inc.eliminado ? "opacity-50" : ""}>
                    <TableCell className="font-medium">{inc.titulo}</TableCell>
                    <TableCell>{inc.tipo_nombre ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant={priorityVariant(inc.prioridad_nivel)}>
                        {inc.prioridad_nivel ?? "—"}
                      </Badge>
                    </TableCell>
                    <TableCell>{inc.estado_nombre ?? "—"}</TableCell>
                    <TableCell>{formatDate(inc.updated_at)}</TableCell>
                    <TableCell>
                      <Link
                        href={`/incidentes/${inc.uuid}`}
                        className="text-teal-400 hover:underline"
                      >
                        Ver
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
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
    </AppShell>
  );
}
