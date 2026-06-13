"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import { listUsuarios } from "@/lib/api/usuarios";
import { useAuthGate } from "@/hooks/useAuthGate";
import {
  canManageUsuarios,
  canViewReportes,
  canViewUsuarios,
  isAdmin,
} from "@/lib/auth/permissions";
import { usePaginatedTable } from "@/hooks/usePaginatedTable";
import { SEDE_LABELS } from "@/lib/constants";
import { AppShell } from "@/components/layout/AppShell";
import { SearchBar } from "@/components/shared/SearchBar";
import { PaginationControls } from "@/components/shared/PaginationControls";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Usuario } from "@/types/usuarios";

export default function UsuariosPage() {
  const { status, user } = useAuthGate(canViewUsuarios);
  const [rows, setRows] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);

  const table = usePaginatedTable(rows, {
    pageSize: 10,
    searchKeys: ["email", "nombre_completo"],
  });

  useEffect(() => {
    if (status !== "ready") {
      setLoading(false);
      return;
    }
    listUsuarios()
      .then(setRows)
      .finally(() => setLoading(false));
  }, [status]);

  if (status === "loading") {
    return (
      <AppShell title="Usuarios">
        <LoadingState />
      </AppShell>
    );
  }

  if (status === "denied") {
    return (
      <AppShell title="Usuarios">
        <AccessDenied />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Usuarios"
      actions={
        canManageUsuarios(user) && (
          <Button asChild>
            <Link href="/usuarios/nuevo">
              <Plus className="h-4 w-4" />
              Nuevo usuario
            </Link>
          </Button>
        )
      }
    >
      {(isAdmin(user) || canViewReportes(user)) && (
        <p className="mb-4 text-sm text-slate-400">
          Vista global: usuarios replicados en ambas sedes (Santa Cruz y Cochabamba). Los cambios se
          sincronizan con LWW.
        </p>
      )}
      <div className="mb-6">
        <SearchBar value={table.search} onChange={table.setSearch} placeholder="Buscar email o nombre..." />
      </div>
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Sede</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.paginated.map((u) => (
                <TableRow key={u.uuid}>
                  <TableCell>{u.nombre_completo}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>{SEDE_LABELS[u.id_sede] ?? u.id_sede}</TableCell>
                  <TableCell>
                    <Badge variant={u.activo ? "success" : "muted"}>
                      {u.activo ? "Activo" : "Inactivo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {canManageUsuarios(user) && (
                      <Link href={`/usuarios/${u.uuid}`} className="text-teal-400 hover:underline">
                        Editar
                      </Link>
                    )}
                  </TableCell>
                </TableRow>
              ))}
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
