"use client";

import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_COLORS } from "@/lib/constants";
import type { ReporteGlobalPayload } from "@/types/reportes";

const tickStyle = { fill: "#94a3b8", fontSize: 12 };
const tooltipContentStyle = {
  background: "#1e293b",
  border: "1px solid #475569",
  borderRadius: "8px",
};

export function ReportesGlobalesPanel({ payload }: { payload: ReporteGlobalPayload }) {
  const dataEstado = payload.incidentes_por_estado.map((i) => ({
    name: i.nombre,
    value: i.cantidad,
  }));
  const dataPrioridad = payload.incidentes_por_prioridad.map((i) => ({
    name: i.nombre,
    value: i.cantidad,
  }));
  const sedesChart = payload.sedes.map((s) => ({
    name: s.nombre_sede.replace(" (Central)", ""),
    incidentes: s.incidentes_total,
    abiertos: s.incidentes_abiertos,
    activos: s.activos_activos,
  }));

  return (
    <>
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-400">Incidentes (todas las sedes)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-slate-100">
              {payload.totales.incidentes ?? 0}
            </p>
            <p className="text-xs text-slate-500">
              {payload.totales.incidentes_abiertos ?? 0} abiertos
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-400">Activos activos</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-400">
              {payload.totales.activos_activos ?? 0}
            </p>
          </CardContent>
        </Card>
        {payload.sedes.map((s) => (
          <Card key={s.id_sede}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-slate-400">{s.nombre_sede}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold text-slate-200">
                {s.incidentes_abiertos} / {s.incidentes_total} inc.
              </p>
              <p className="text-xs text-slate-500">
                {s.activos_activos} activos · nodo {s.nodo}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="border-blue-800/40 bg-blue-950/20">
          <CardHeader>
            <CardTitle className="text-blue-300">Incidentes por sede</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sedesChart}>
                <XAxis dataKey="name" tick={tickStyle} />
                <YAxis tick={tickStyle} />
                <Tooltip contentStyle={tooltipContentStyle} />
                <Legend />
                <Bar dataKey="incidentes" fill="#36A2EB" name="Total" />
                <Bar dataKey="abiertos" fill="#FF9F40" name="Abiertos" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-emerald-800/40 bg-emerald-950/20">
          <CardHeader>
            <CardTitle className="text-emerald-300">Por estado (global)</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dataEstado} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {dataEstado.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipContentStyle} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-orange-800/40 bg-orange-950/20 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-orange-300">Por prioridad (global)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dataPrioridad} layout="vertical">
                <XAxis type="number" tick={tickStyle} />
                <YAxis type="category" dataKey="name" width={100} tick={tickStyle} />
                <Tooltip contentStyle={tooltipContentStyle} />
                <Bar dataKey="value" fill="#FF6384" name="Incidentes" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
