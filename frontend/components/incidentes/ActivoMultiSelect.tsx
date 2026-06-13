"use client";

import { useEffect, useState } from "react";
import { listActivos } from "@/lib/api/activos";
import { Label } from "@/components/ui/label";
import type { Activo } from "@/types/activos";

type Props = {
  selected: string[];
  onChange: (uuids: string[]) => void;
};

export function ActivoMultiSelect({ selected, onChange }: Props) {
  const [activos, setActivos] = useState<Activo[]>([]);

  useEffect(() => {
    listActivos().then(setActivos).catch(() => setActivos([]));
  }, []);

  const toggle = (uuid: string) => {
    if (selected.includes(uuid)) {
      onChange(selected.filter((id) => id !== uuid));
    } else {
      onChange([...selected, uuid]);
    }
  };

  if (activos.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No hay activos en esta sede. Puedes vincularlos después desde el detalle.
      </p>
    );
  }

  return (
    <div>
      <Label>Activos afectados (opcional)</Label>
      <div className="mt-2 max-h-40 space-y-2 overflow-y-auto rounded-lg border border-slate-700 p-3">
        {activos.map((a) => (
          <label
            key={a.uuid}
            className="flex cursor-pointer items-center gap-2 text-sm text-slate-300"
          >
            <input
              type="checkbox"
              checked={selected.includes(a.uuid)}
              onChange={() => toggle(a.uuid)}
              className="rounded border-slate-600"
            />
            <span>
              {a.hostname}
              {a.tipo_activo ? ` · ${a.tipo_activo}` : ""}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
