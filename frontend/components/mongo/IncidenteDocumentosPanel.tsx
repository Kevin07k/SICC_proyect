"use client";

import { useCallback, useEffect, useState } from "react";
import { Database, Plus, Trash2 } from "lucide-react";
import {
  createEvidencia,
  createTimeline,
  listEvidencias,
  listTimeline,
} from "@/lib/api/mongo";
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
import type { Evidencia, EvidenciaCreate, TimelineEvento } from "@/types/mongo";

type Tab = "evidencias" | "timeline";
type EvidenciaTipo = "ioc" | "log" | "adjunto" | "captura";

type IocRow = { tipo: string; valor: string };

const EVIDENCIA_TIPOS: { value: EvidenciaTipo; label: string; hint: string }[] = [
  {
    value: "ioc",
    label: "IoC (indicadores)",
    hint: "Varios indicadores en un mismo documento: IP, dominio, hash…",
  },
  {
    value: "log",
    label: "Log",
    hint: "Una línea por renglón; opcional fuente y asunto en metadata.",
  },
  {
    value: "adjunto",
    label: "Adjunto",
    hint: "Metadatos de archivo (nombre, MIME, hash) como en el seed demo.",
  },
  {
    value: "captura",
    label: "Captura / alerta",
    hint: "Metadata de alerta (fuente, descripción) y opcional un IoC.",
  },
];

function emptyIocRow(): IocRow {
  return { tipo: "ip", valor: "" };
}

export function IncidenteDocumentosPanel({
  incidenteUuid,
  canManage,
}: {
  incidenteUuid: string;
  canManage: boolean;
}) {
  const { toast } = useToast();
  const [tab, setTab] = useState<Tab>("evidencias");
  const [evidencias, setEvidencias] = useState<Evidencia[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvento[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [evTipo, setEvTipo] = useState<EvidenciaTipo>("ioc");
  const [iocRows, setIocRows] = useState<IocRow[]>([emptyIocRow(), emptyIocRow()]);
  const [logLineas, setLogLineas] = useState("");
  const [metaFuente, setMetaFuente] = useState("");
  const [metaSeveridad, setMetaSeveridad] = useState("");
  const [metaAsunto, setMetaAsunto] = useState("");
  const [metaDescripcion, setMetaDescripcion] = useState("");
  const [adjNombre, setAdjNombre] = useState("");
  const [adjMime, setAdjMime] = useState("application/octet-stream");
  const [adjHash, setAdjHash] = useState("");

  const [tlTipo, setTlTipo] = useState("nota_analista");
  const [tlTexto, setTlTexto] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [ev, tl] = await Promise.all([
        listEvidencias(incidenteUuid),
        listTimeline(incidenteUuid),
      ]);
      setEvidencias(ev);
      setTimeline(tl);
    } catch (err) {
      toast(
        "MongoDB",
        err instanceof ApiError ? err.message : "No se pudieron cargar documentos",
        "error",
      );
    } finally {
      setLoading(false);
    }
  }, [incidenteUuid, toast]);

  useEffect(() => {
    load();
  }, [load]);

  const buildMetadata = (): Record<string, string> | undefined => {
    const meta: Record<string, string> = {};
    if (metaFuente.trim()) meta.fuente = metaFuente.trim();
    if (metaSeveridad.trim()) meta.severidad_detectada = metaSeveridad.trim();
    if (metaAsunto.trim()) meta.asunto = metaAsunto.trim();
    if (metaDescripcion.trim()) meta.descripcion = metaDescripcion.trim();
    if (adjNombre.trim()) meta.nombre_archivo = adjNombre.trim();
    if (adjMime.trim()) meta.mime = adjMime.trim();
    if (adjHash.trim()) meta.hash_sha256 = adjHash.trim();
    return Object.keys(meta).length > 0 ? meta : undefined;
  };

  const buildEvidenciaBody = (): EvidenciaCreate | null => {
    if (evTipo === "ioc") {
      const iocs = iocRows
        .filter((r) => r.valor.trim())
        .map((r) => ({ tipo: r.tipo.trim(), valor: r.valor.trim() }));
      if (iocs.length === 0) return null;
      return { tipo: "ioc", iocs, metadata: buildMetadata() };
    }
    if (evTipo === "log") {
      const lineas = logLineas
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);
      if (lineas.length === 0) return null;
      return { tipo: "log", lineas, metadata: buildMetadata() };
    }
    if (evTipo === "adjunto") {
      if (!adjNombre.trim() && !adjHash.trim()) return null;
      return { tipo: "adjunto", metadata: buildMetadata() };
    }
    if (evTipo === "captura") {
      const iocs = iocRows
        .filter((r) => r.valor.trim())
        .map((r) => ({ tipo: r.tipo.trim(), valor: r.valor.trim() }));
      const metadata = buildMetadata();
      if (!metadata && iocs.length === 0) return null;
      return {
        tipo: "captura",
        metadata,
        iocs: iocs.length > 0 ? iocs : undefined,
      };
    }
    return null;
  };

  const resetEvidenciaForm = () => {
    setIocRows([emptyIocRow(), emptyIocRow()]);
    setLogLineas("");
    setMetaFuente("");
    setMetaSeveridad("");
    setMetaAsunto("");
    setMetaDescripcion("");
    setAdjNombre("");
    setAdjMime("application/octet-stream");
    setAdjHash("");
  };

  const handleAddEvidencia = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = buildEvidenciaBody();
    if (!body) {
      toast("Completa los campos", "Faltan datos obligatorios para este tipo", "error");
      return;
    }
    setSubmitting(true);
    try {
      await createEvidencia(incidenteUuid, body);
      resetEvidenciaForm();
      toast("Evidencia registrada en MongoDB");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddTimeline = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tlTexto.trim()) return;
    try {
      await createTimeline(incidenteUuid, {
        tipo_evento: tlTipo,
        payload: { texto: tlTexto.trim() },
      });
      setTlTexto("");
      toast("Evento añadido al timeline");
      load();
    } catch (err) {
      toast("Error", err instanceof ApiError ? err.message : "Error", "error");
    }
  };

  const updateIocRow = (index: number, patch: Partial<IocRow>) => {
    setIocRows((rows) => rows.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  };

  const tipoHint = EVIDENCIA_TIPOS.find((t) => t.value === evTipo)?.hint;

  return (
    <Card className="border-emerald-900/40 bg-emerald-950/10">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-emerald-300">
          <Database className="h-5 w-5" />
          Documentos NoSQL (MongoDB)
        </CardTitle>
        <p className="text-xs text-slate-500">
          Evidencias e IoCs · Timeline de investigación · Sede local
        </p>
        <div className="mt-2 flex gap-2">
          <Button
            type="button"
            size="sm"
            variant={tab === "evidencias" ? "default" : "secondary"}
            onClick={() => setTab("evidencias")}
          >
            Evidencias ({evidencias.length})
          </Button>
          <Button
            type="button"
            size="sm"
            variant={tab === "timeline" ? "default" : "secondary"}
            onClick={() => setTab("timeline")}
          >
            Timeline ({timeline.length})
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading ? (
          <p className="text-sm text-slate-500">Cargando documentos...</p>
        ) : tab === "evidencias" ? (
          <>
            {canManage && (
              <form
                onSubmit={handleAddEvidencia}
                className="space-y-4 rounded-lg border border-slate-700 p-4"
              >
                <div>
                  <Label>Tipo de evidencia</Label>
                  <Select
                    value={evTipo}
                    onValueChange={(v) => {
                      setEvTipo(v as EvidenciaTipo);
                      resetEvidenciaForm();
                    }}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EVIDENCIA_TIPOS.map((t) => (
                        <SelectItem key={t.value} value={t.value}>
                          {t.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {tipoHint && (
                    <p className="mt-1 text-xs text-slate-500">{tipoHint}</p>
                  )}
                </div>

                {(evTipo === "ioc" || evTipo === "captura") && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Indicadores (IoCs)</Label>
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        onClick={() => setIocRows((r) => [...r, emptyIocRow()])}
                      >
                        <Plus className="h-3 w-3" />
                        Agregar IoC
                      </Button>
                    </div>
                    {iocRows.map((row, i) => (
                      <div key={i} className="flex gap-2">
                        <Input
                          className="w-32"
                          placeholder="tipo"
                          value={row.tipo}
                          onChange={(e) => updateIocRow(i, { tipo: e.target.value })}
                        />
                        <Input
                          className="flex-1"
                          placeholder="valor (IP, dominio, hash…)"
                          value={row.valor}
                          onChange={(e) => updateIocRow(i, { valor: e.target.value })}
                        />
                        {iocRows.length > 1 && (
                          <Button
                            type="button"
                            size="icon"
                            variant="secondary"
                            onClick={() =>
                              setIocRows((rows) => rows.filter((_, j) => j !== i))
                            }
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {evTipo === "log" && (
                  <div>
                    <Label>Líneas de log (una por renglón)</Label>
                    <textarea
                      className="mt-1 min-h-[100px] w-full rounded-lg border border-slate-600 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      placeholder={"2026-06-01T08:15:00Z Usuario abrio enlace\n2026-06-01T08:16:12Z Proxy bloqueo descarga"}
                      value={logLineas}
                      onChange={(e) => setLogLineas(e.target.value)}
                    />
                  </div>
                )}

                {evTipo === "adjunto" && (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <Label>Nombre de archivo</Label>
                      <Input
                        className="mt-1"
                        placeholder="factura_junio.pdf.exe"
                        value={adjNombre}
                        onChange={(e) => setAdjNombre(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label>MIME</Label>
                      <Input
                        className="mt-1"
                        value={adjMime}
                        onChange={(e) => setAdjMime(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label>Hash SHA256</Label>
                      <Input
                        className="mt-1"
                        placeholder="64 caracteres hex"
                        value={adjHash}
                        onChange={(e) => setAdjHash(e.target.value)}
                      />
                    </div>
                  </div>
                )}

                {(evTipo === "ioc" || evTipo === "log" || evTipo === "captura") && (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <Label>Fuente (metadata)</Label>
                      <Input
                        className="mt-1"
                        placeholder="EDR, correo, IDS…"
                        value={metaFuente}
                        onChange={(e) => setMetaFuente(e.target.value)}
                      />
                    </div>
                    {(evTipo === "ioc" || evTipo === "captura") && (
                      <div>
                        <Label>Severidad (metadata)</Label>
                        <Input
                          className="mt-1"
                          placeholder="baja, media, alta"
                          value={metaSeveridad}
                          onChange={(e) => setMetaSeveridad(e.target.value)}
                        />
                      </div>
                    )}
                    {evTipo === "log" && (
                      <div>
                        <Label>Asunto (metadata)</Label>
                        <Input
                          className="mt-1"
                          placeholder="Asunto del correo o alerta"
                          value={metaAsunto}
                          onChange={(e) => setMetaAsunto(e.target.value)}
                        />
                      </div>
                    )}
                    {evTipo === "captura" && (
                      <div className="sm:col-span-2">
                        <Label>Descripción (metadata)</Label>
                        <Input
                          className="mt-1"
                          placeholder="Detalle de la captura o alerta"
                          value={metaDescripcion}
                          onChange={(e) => setMetaDescripcion(e.target.value)}
                        />
                      </div>
                    )}
                  </div>
                )}

                <div className="flex justify-end">
                  <Button type="submit" disabled={submitting}>
                    {submitting ? "Guardando…" : "Registrar evidencia"}
                  </Button>
                </div>
              </form>
            )}
            <div className="space-y-3">
              {evidencias.length === 0 && (
                <p className="text-sm text-slate-500">Sin evidencias documentales.</p>
              )}
              {evidencias.map((ev) => (
                <div key={ev.id} className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <Badge variant="muted">{ev.tipo}</Badge>
                    <span className="text-xs text-slate-500">{formatDate(ev.created_at)}</span>
                  </div>
                  {ev.iocs && ev.iocs.length > 0 && (
                    <ul className="space-y-1 text-sm text-slate-300">
                      {ev.iocs.map((ioc, i) => (
                        <li key={i}>
                          <span className="text-slate-500">{String(ioc.tipo)}:</span>{" "}
                          {String(ioc.valor)}
                        </li>
                      ))}
                    </ul>
                  )}
                  {ev.lineas && ev.lineas.length > 0 && (
                    <pre className="mt-2 overflow-x-auto text-xs text-slate-400">
                      {ev.lineas.join("\n")}
                    </pre>
                  )}
                  {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                    <pre className="mt-2 overflow-x-auto text-xs text-slate-400">
                      {JSON.stringify(ev.metadata, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            {canManage && (
              <form onSubmit={handleAddTimeline} className="space-y-3 rounded-lg border border-slate-700 p-4">
                <div>
                  <Label>Tipo de evento</Label>
                  <Input className="mt-1" value={tlTipo} onChange={(e) => setTlTipo(e.target.value)} />
                </div>
                <div>
                  <Label>Detalle</Label>
                  <Input
                    className="mt-1"
                    placeholder="Descripción del evento..."
                    value={tlTexto}
                    onChange={(e) => setTlTexto(e.target.value)}
                  />
                </div>
                <Button type="submit">Registrar evento</Button>
              </form>
            )}
            <div className="relative space-y-0 border-l border-emerald-800/50 pl-4">
              {timeline.length === 0 && (
                <p className="text-sm text-slate-500">Sin eventos en timeline.</p>
              )}
              {timeline.map((ev) => (
                <div key={ev.id} className="relative pb-6 last:pb-0">
                  <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-emerald-500" />
                  <p className="text-sm font-medium text-slate-200">{ev.tipo_evento}</p>
                  <p className="text-sm text-slate-400">
                    {typeof ev.payload.texto === "string"
                      ? ev.payload.texto
                      : JSON.stringify(ev.payload)}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">{formatDate(ev.created_at)}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
