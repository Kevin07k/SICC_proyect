"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, ArrowRightLeft } from "lucide-react";
import { listActivos } from "@/lib/api/activos";
import { listSedes } from "@/lib/api/catalogos";
import { transferirActivo } from "@/lib/api/activos";
import { useAuthGate } from "@/hooks/useAuthGate";
import { canManageActivos, canViewActivos } from "@/lib/auth/permissions";
import { usePaginatedTable } from "@/hooks/usePaginatedTable";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/layout/AppShell";
import { SearchBar } from "@/components/shared/SearchBar";
import { PaginationControls } from "@/components/shared/PaginationControls";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toaster";
import type { Activo } from "@/types/activos";
import type { Sede } from "@/types/catalogos";

export default function ActivosPage() {
  const { status, user } = useAuthGate(canViewActivos);
  const { toast } = useToast();
  const [rows, setRows] = useState<Activo[]>([]);
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [loading, setLoading] = useState(true);
  const [transferUuid, setTransferUuid] = useState<string | null>(null);
  const [sedeDestino, setSedeDestino] = useState("");
  const [motivo, setMotivo] = useState("");

  const table = usePaginatedTable(rows, {
    pageSize: 10,
    searchKeys: ["hostname", "direccion_ip", "tipo_activo", "propietario"],
  });

  const load = () => {
    listActivos()
      .then(setRows)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (status !== "ready") {
      setLoading(false);
      return;
    }
    load();
    listSedes().then(setSedes).catch(() => {});
  }, [status]);

  const handleTransfer = async () => {
    if (!transferUuid || !sedeDestino || motivo.length < 3) return;
    try {
      await transferirActivo(transferUuid, {
        sede_destino_id: Number(sedeDestino),
        motivo,
      });
      toast("Activo transferido");
      setTransferUuid(null);
      setMotivo("");
      setSedeDestino("");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    }
  };

  if (status === "loading") {
    return (
      <AppShell title="Activos">
        <LoadingState />
      </AppShell>
    );
  }

  if (status === "denied") {
    return (
      <AppShell title="Activos">
        <AccessDenied />
      </AppShell>
    );
  }

  const sedesDestino = sedes.filter((s) => s.id_sede !== user?.id_sede && !s.eliminado);

  return (
    <AppShell
      title="Activos"
      actions={
        canManageActivos(user) && (
          <Button asChild>
            <Link href="/activos/nuevo">
              <Plus className="h-4 w-4" />
              Nuevo activo
            </Link>
          </Button>
        )
      }
    >
      <div className="mb-6">
        <SearchBar
          value={table.search}
          onChange={table.setSearch}
          placeholder="Buscar hostname, IP, tipo..."
        />
      </div>
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hostname</TableHead>
                <TableHead>IP</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Propietario</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.paginated.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-slate-500">
                    Sin activos
                  </TableCell>
                </TableRow>
              ) : (
                table.paginated.map((a) => (
                  <TableRow key={a.uuid} className={a.eliminado ? "opacity-50" : ""}>
                    <TableCell className="font-medium">{a.hostname}</TableCell>
                    <TableCell>{a.direccion_ip ?? "—"}</TableCell>
                    <TableCell>{a.tipo_activo ?? "—"}</TableCell>
                    <TableCell>{a.propietario ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant={a.eliminado ? "muted" : "success"}>
                        {a.eliminado ? "Baja" : "Activo"}
                      </Badge>
                    </TableCell>
                    <TableCell className="space-x-2">
                      <Link
                        href={`/activos/${a.uuid}`}
                        className="text-teal-400 hover:underline"
                      >
                        {canManageActivos(user) ? "Editar" : "Ver"}
                      </Link>
                      {canManageActivos(user) && !a.eliminado && sedesDestino.length > 0 && (
                        <Dialog
                          open={transferUuid === a.uuid}
                          onOpenChange={(o) => !o && setTransferUuid(null)}
                        >
                          <DialogTrigger asChild>
                            <button
                              type="button"
                              className="text-indigo-400 hover:underline"
                              onClick={() => setTransferUuid(a.uuid)}
                            >
                              <ArrowRightLeft className="inline h-3 w-3" /> Trasladar
                            </button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Trasladar {a.hostname}</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <Label>Sede destino</Label>
                                <Select value={sedeDestino} onValueChange={setSedeDestino}>
                                  <SelectTrigger className="mt-1">
                                    <SelectValue placeholder="Seleccionar sede" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {sedesDestino.map((s) => (
                                      <SelectItem
                                        key={s.id_sede}
                                        value={String(s.id_sede)}
                                      >
                                        {s.nombre_sede}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div>
                                <Label>Motivo</Label>
                                <Input
                                  className="mt-1"
                                  value={motivo}
                                  onChange={(e) => setMotivo(e.target.value)}
                                  minLength={3}
                                />
                              </div>
                              <Button onClick={handleTransfer}>Confirmar traslado</Button>
                            </div>
                          </DialogContent>
                        </Dialog>
                      )}
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
