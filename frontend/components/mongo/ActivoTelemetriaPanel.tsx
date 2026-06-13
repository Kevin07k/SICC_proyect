"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Plus, Trash2 } from "lucide-react";
import { createTelemetria, listTelemetria } from "@/lib/api/mongo";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import type { Telemetria, TelemetriaCreate } from "@/types/mongo";

type TipoEscaneo = "vulnerabilidades" | "configuracion";

type HallazgoRow = {
  severidad: string;
  descripcion: string;
  cve: string;
};

const TIPOS: { value: TipoEscaneo; label: string; hint: string }[] = [
  {
    value: "vulnerabilidades",
    label: "Vulnerabilidades",
    hint: "Hallazgos con CVE opcional + snapshot de OS / parches.",
  },
  {
    value: "configuracion",
    label: "Configuración",
    hint: "Hallazgos de hardening + snapshot (motor, backups, servicios…).",
  },
];

function emptyHallazgo(): HallazgoRow {
  return { severidad: "media", descripcion: "", cve: "" };
}

export function ActivoTelemetriaPanel({
  activoUuid,
  canManage,
}: {
  activoUuid: string;
  canManage: boolean;
}) {
  const { toast } = useToast();
  const [items, setItems] = useState<Telemetria[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [tipoEscaneo, setTipoEscaneo] = useState<TipoEscaneo>("configuracion");
  const [hallazgos, setHallazgos] = useState<HallazgoRow[]>([emptyHallazgo()]);
  const [snapOs, setSnapOs] = useState("");
  const [snapHostname, setSnapHostname] = useState("");
  const [snapMotor, setSnapMotor] = useState("");
  const [snapBackups, setSnapBackups] = useState("");
  const [snapFirmware, setSnapFirmware] = useState("");
  const [snapReglas, setSnapReglas] = useState("");
  const [snapParches, setSnapParches] = useState("");
  const [snapServicios, setSnapServicios] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listTelemetria(activoUuid);
      setItems(data);
    } catch (err) {
      toast(
        "MongoDB",
        err instanceof ApiError ? err.message : "No se pudo cargar telemetría",
        "error",
      );
    } finally {
      setLoading(false);
    }
  }, [activoUuid, toast]);

  useEffect(() => {
    load();
  }, [load]);

  const buildSnapshot = (): Record<string, unknown> | undefined => {
    const snap: Record<string, unknown> = {};
    if (snapOs.trim()) snap.os = snapOs.trim();
    if (snapHostname.trim()) snap.hostname = snapHostname.trim();
    if (snapMotor.trim()) snap.motor = snapMotor.trim();
    if (snapBackups.trim()) snap.backups = snapBackups.trim();
    if (snapFirmware.trim()) snap.firmware = snapFirmware.trim();
    if (snapReglas.trim()) {
      const n = Number(snapReglas);
      snap.reglas_activas = Number.isNaN(n) ? snapReglas.trim() : n;
    }
    if (snapParches.trim()) {
      const n = Number(snapParches);
      snap.parches_pendientes = Number.isNaN(n) ? snapParches.trim() : n;
    }
    if (snapServicios.trim()) {
      snap.servicios = snapServicios.split(",").map((s) => s.trim()).filter(Boolean);
    }
    return Object.keys(snap).length > 0 ? snap : undefined;
  };

  const buildBody = (): TelemetriaCreate | null => {
    const rows = hallazgos
      .filter((h) => h.descripcion.trim())
      .map((h) => {
        const item: Record<string, string> = {
          severidad: h.severidad.trim(),
          descripcion: h.descripcion.trim(),
        };
        if (h.cve.trim()) item.cve = h.cve.trim();
        return item;
      });
    const snapshot = buildSnapshot();
    if (rows.length === 0 && !snapshot) return null;
    return {
      tipo_escaneo: tipoEscaneo,
      hallazgos: rows.length > 0 ? rows : undefined,
      snapshot,
    };
  };

  const resetForm = () => {
    setHallazgos([emptyHallazgo()]);
    setSnapOs("");
    setSnapHostname("");
    setSnapMotor("");
    setSnapBackups("");
    setSnapFirmware("");
    setSnapReglas("");
    setSnapParches("");
    setSnapServicios("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = buildBody();
    if (!body) {
      toast("Completa los campos", "Al menos un hallazgo o dato de snapshot", "error");
      return;
    }
    setSubmitting(true);
    try {
      await createTelemetria(activoUuid, body);
      resetForm();
      toast("Telemetría registrada en MongoDB");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const updateHallazgo = (index: number, patch: Partial<HallazgoRow>) => {
    setHallazgos((rows) => rows.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  };

  const tipoHint = TIPOS.find((t) => t.value === tipoEscaneo)?.hint;

  return (
    <Card className="mt-8 border-emerald-900/40 bg-emerald-950/10">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-emerald-300">
          <Activity className="h-5 w-5" />
          Telemetría NoSQL (MongoDB)
        </CardTitle>
        <p className="text-xs text-slate-500">
          Escaneos, hallazgos y snapshots técnicos del activo en la sede local
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {canManage && (
          <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-700 p-4">
            <div>
              <Label>Tipo de escaneo</Label>
              <Select
                value={tipoEscaneo}
                onValueChange={(v) => {
                  setTipoEscaneo(v as TipoEscaneo);
                  resetForm();
                }}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIPOS.map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {tipoHint && <p className="mt-1 text-xs text-slate-500">{tipoHint}</p>}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Hallazgos</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  onClick={() => setHallazgos((r) => [...r, emptyHallazgo()])}
                >
                  <Plus className="h-3 w-3" />
                  Agregar hallazgo
                </Button>
              </div>
              {hallazgos.map((h, i) => (
                <div key={i} className="grid gap-2 rounded-md border border-slate-700/80 p-3 sm:grid-cols-12">
                  <div className="sm:col-span-2">
                    <Label className="text-xs">Severidad</Label>
                    <Input
                      className="mt-1"
                      placeholder="baja, media, alta"
                      value={h.severidad}
                      onChange={(e) => updateHallazgo(i, { severidad: e.target.value })}
                    />
                  </div>
                  {tipoEscaneo === "vulnerabilidades" && (
                    <div className="sm:col-span-3">
                      <Label className="text-xs">CVE (opcional)</Label>
                      <Input
                        className="mt-1"
                        placeholder="CVE-2024-0100"
                        value={h.cve}
                        onChange={(e) => updateHallazgo(i, { cve: e.target.value })}
                      />
                    </div>
                  )}
                  <div className={tipoEscaneo === "vulnerabilidades" ? "sm:col-span-6" : "sm:col-span-9"}>
                    <Label className="text-xs">Descripción</Label>
                    <Input
                      className="mt-1"
                      placeholder="Replica MySQL sincronizada, parche pendiente…"
                      value={h.descripcion}
                      onChange={(e) => updateHallazgo(i, { descripcion: e.target.value })}
                    />
                  </div>
                  <div className="flex items-end sm:col-span-1">
                    {hallazgos.length > 1 && (
                      <Button
                        type="button"
                        size="icon"
                        variant="secondary"
                        onClick={() => setHallazgos((rows) => rows.filter((_, j) => j !== i))}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              <Label>Snapshot técnico (opcional)</Label>
              {tipoEscaneo === "configuracion" ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <Label className="text-xs">Motor</Label>
                    <Input
                      className="mt-1"
                      placeholder="MySQL 8.0"
                      value={snapMotor}
                      onChange={(e) => setSnapMotor(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Backups</Label>
                    <Input
                      className="mt-1"
                      placeholder="diarios"
                      value={snapBackups}
                      onChange={(e) => setSnapBackups(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Firmware</Label>
                    <Input
                      className="mt-1"
                      placeholder="12.1.3"
                      value={snapFirmware}
                      onChange={(e) => setSnapFirmware(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Reglas activas</Label>
                    <Input
                      className="mt-1"
                      placeholder="142"
                      value={snapReglas}
                      onChange={(e) => setSnapReglas(e.target.value)}
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <Label className="text-xs">Servicios (separados por coma)</Label>
                    <Input
                      className="mt-1"
                      placeholder="sshd, nginx"
                      value={snapServicios}
                      onChange={(e) => setSnapServicios(e.target.value)}
                    />
                  </div>
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <Label className="text-xs">Sistema operativo</Label>
                    <Input
                      className="mt-1"
                      placeholder="Windows 10, Linux…"
                      value={snapOs}
                      onChange={(e) => setSnapOs(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Hostname</Label>
                    <Input
                      className="mt-1"
                      placeholder="cb-srv-01.demo"
                      value={snapHostname}
                      onChange={(e) => setSnapHostname(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Parches pendientes</Label>
                    <Input
                      className="mt-1"
                      placeholder="3"
                      value={snapParches}
                      onChange={(e) => setSnapParches(e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Guardando…" : "Registrar telemetría"}
              </Button>
            </div>
          </form>
        )}
        {loading ? (
          <p className="text-sm text-slate-500">Cargando telemetría...</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-slate-500">Sin registros de telemetría.</p>
        ) : (
          <div className="space-y-3">
            {items.map((t) => (
              <div key={t.id} className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant="muted">{t.tipo_escaneo}</Badge>
                  <span className="text-xs text-slate-500">{formatDate(t.captured_at)}</span>
                </div>
                {t.hallazgos && t.hallazgos.length > 0 && (
                  <ul className="space-y-1 text-sm text-slate-300">
                    {t.hallazgos.map((h, i) => (
                      <li key={i}>
                        <Badge variant="default" className="mr-2">
                          {String(h.severidad ?? "—")}
                        </Badge>
                        {h.cve ? (
                          <span className="text-slate-500">{String(h.cve)} · </span>
                        ) : null}
                        {String(h.descripcion ?? JSON.stringify(h))}
                      </li>
                    ))}
                  </ul>
                )}
                {t.snapshot && Object.keys(t.snapshot).length > 0 && (
                  <pre className="mt-2 overflow-x-auto text-xs text-slate-400">
                    {JSON.stringify(t.snapshot, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
