"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus, Pencil, Trash2 } from "lucide-react";
import {
  createTipoIncidente,
  deleteTipoIncidente,
  listTiposIncidenteGestion,
  updateTipoIncidente,
} from "@/lib/api/catalogos";
import { useAuthGate } from "@/hooks/useAuthGate";
import { canManageTiposIncidente } from "@/lib/auth/permissions";
import { AppShell } from "@/components/layout/AppShell";
import { LoadingState } from "@/components/shared/LoadingState";
import { AccessDenied } from "@/components/shared/AccessDenied";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError } from "@/lib/api/client";
import { useToast } from "@/components/ui/toaster";
import type { TipoIncidente } from "@/types/catalogos";

export default function TiposIncidenteAdminPage() {
  const { status } = useAuthGate(canManageTiposIncidente);
  const { toast } = useToast();
  const [rows, setRows] = useState<TipoIncidente[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState<TipoIncidente | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    listTiposIncidenteGestion()
      .then(setRows)
      .catch((err) =>
        toast("Error", err instanceof ApiError ? err.message : "No se pudo cargar", "error"),
      )
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => {
    if (status === "ready") load();
  }, [status, load]);

  const resetForm = () => {
    setEditing(null);
    setNombre("");
    setDescripcion("");
    setShowForm(false);
  };

  const openCreate = () => {
    setEditing(null);
    setNombre("");
    setDescripcion("");
    setShowForm(true);
  };

  const openEdit = (row: TipoIncidente) => {
    setEditing(row);
    setNombre(row.nombre);
    setDescripcion(row.descripcion ?? "");
    setShowForm(true);
  };

  const handleSubmit = async () => {
    if (!nombre.trim()) {
      toast("Validación", "El nombre es obligatorio", "error");
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await updateTipoIncidente(editing.id_tipo, {
          nombre: nombre.trim(),
          descripcion: descripcion.trim() || null,
        });
        toast("Actualizado", "Tipo de incidente modificado. Ejecuta sync para replicar.");
      } else {
        await createTipoIncidente({
          nombre: nombre.trim(),
          descripcion: descripcion.trim() || null,
        });
        toast("Creado", "Tipo agregado en central. Ejecuta sync para replicar a Cochabamba.");
      }
      resetForm();
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo guardar", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (row: TipoIncidente) => {
    if (row.eliminado) return;
    if (!confirm(`¿Dar de baja el tipo "${row.nombre}"?`)) return;
    try {
      await deleteTipoIncidente(row.id_tipo);
      toast("Baja lógica", "Tipo desactivado. Ejecuta sync si aplica.");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "No se pudo eliminar", "error");
    }
  };

  if (status === "loading") {
    return (
      <AppShell title="Tipos de incidente">
        <LoadingState />
      </AppShell>
    );
  }

  if (status === "denied") {
    return (
      <AppShell title="Tipos de incidente">
        <AccessDenied message="Solo sede central con permiso catalogos.gestionar (DBA/Admin)." />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Tipos de incidente"
      actions={
        !showForm && (
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            Nuevo tipo
          </Button>
        )
      }
    >
      <p className="mb-4 text-sm text-slate-400">
        Catálogo maestro en sede central. Tras crear o modificar, ejecuta{" "}
        <strong className="text-slate-300">Sincronización</strong> para replicar metadata en
        Cochabamba.
      </p>

      {showForm && (
        <div className="mb-6 rounded-lg border border-slate-700 bg-slate-800/50 p-4">
          <h3 className="mb-3 text-lg font-semibold text-slate-100">
            {editing ? "Editar tipo" : "Nuevo tipo"}
          </h3>
          <div className="grid max-w-lg gap-4">
            <div>
              <Label htmlFor="nombre">Nombre</Label>
              <Input
                id="nombre"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                maxLength={100}
              />
            </div>
            <div>
              <Label htmlFor="descripcion">Descripción</Label>
              <Input
                id="descripcion"
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                maxLength={500}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} disabled={saving}>
                {saving ? "Guardando…" : "Guardar"}
              </Button>
              <Button variant="outline" onClick={resetForm} disabled={saving}>
                Cancelar
              </Button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <LoadingState />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Nombre</TableHead>
              <TableHead>Descripción</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id_tipo}>
                <TableCell>{row.id_tipo}</TableCell>
                <TableCell className="font-medium">{row.nombre}</TableCell>
                <TableCell className="text-slate-400">{row.descripcion ?? "—"}</TableCell>
                <TableCell>
                  {row.eliminado ? (
                    <Badge variant="destructive">Baja</Badge>
                  ) : (
                    <Badge variant="default">Activo</Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {!row.eliminado && (
                    <div className="flex justify-end gap-2">
                      <Button size="sm" variant="outline" onClick={() => openEdit(row)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(row)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </AppShell>
  );
}
