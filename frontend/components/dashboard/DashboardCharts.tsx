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
import type { Incidente } from "@/types/incidentes";
import type { Activo } from "@/types/activos";

function countBy<T>(items: T[], keyFn: (item: T) => string | null | undefined) {
  const map = new Map<string, number>();
  for (const item of items) {
    const k = keyFn(item) ?? "Sin dato";
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
}

export function DashboardCharts({
  incidentes,
  activos,
}: {
  incidentes: Incidente[];
  activos: Activo[];
}) {
  const incActivos = incidentes.filter((i) => !i.eliminado);
  const dataPrioridad = countBy(incActivos, (i) => i.prioridad_nivel);
  const dataTipo = countBy(incActivos, (i) => i.tipo_nombre);
  const dataEstado = countBy(incActivos, (i) => i.estado_nombre);
  const activosActivos = activos.filter((a) => !a.eliminado);
  const activosBaja = activos.filter((a) => a.eliminado);

  const activosChart = [
    { name: "Activos", value: activosActivos.length },
    { name: "Baja lógica", value: activosBaja.length },
  ];

  const tickStyle = { fill: "#94a3b8", fontSize: 12 };
  const tooltipContentStyle = {
    background: "#1e293b",
    border: "1px solid #475569",
    borderRadius: "8px",
  };
  const tooltipLabelStyle = { color: "#f1f5f9" };

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <Card className="border-blue-800/40 bg-blue-950/20">
        <CardHeader>
          <CardTitle className="text-blue-300">Por prioridad</CardTitle>
        </CardHeader>
        <CardContent className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={dataPrioridad} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}>
                {dataPrioridad.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipContentStyle} labelStyle={tooltipLabelStyle} />
              <Legend wrapperStyle={{ color: "#94a3b8" }} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="border-green-800/40 bg-green-950/20">
        <CardHeader>
          <CardTitle className="text-green-300">Por tipo</CardTitle>
        </CardHeader>
        <CardContent className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={dataTipo} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}>
                {dataTipo.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[(i + 2) % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipContentStyle} labelStyle={tooltipLabelStyle} />
              <Legend wrapperStyle={{ color: "#94a3b8" }} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="border-yellow-800/40 bg-yellow-950/20">
        <CardHeader>
          <CardTitle className="text-yellow-300">Por estado</CardTitle>
        </CardHeader>
        <CardContent className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dataEstado}>
              <XAxis dataKey="name" tick={tickStyle} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={tickStyle} />
              <Tooltip contentStyle={tooltipContentStyle} labelStyle={tooltipLabelStyle} />
              <Bar dataKey="value" fill="#FFCD56" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="border-purple-800/40 bg-purple-950/20">
        <CardHeader>
          <CardTitle className="text-purple-300">Activos en sede</CardTitle>
        </CardHeader>
        <CardContent className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={activosChart} layout="vertical">
              <XAxis type="number" tick={tickStyle} />
              <YAxis type="category" dataKey="name" tick={tickStyle} width={90} />
              <Tooltip contentStyle={tooltipContentStyle} labelStyle={tooltipLabelStyle} />
              <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
