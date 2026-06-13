import { api } from "@/lib/api/client";
import type {
  Activo,
  ActivoCreate,
  ActivoTransferirRequest,
  ActivoTransferirResponse,
  ActivoUpdate,
} from "@/types/activos";

export function listActivos(): Promise<Activo[]> {
  return api<Activo[]>("/activos");
}

export function getActivo(uuid: string): Promise<Activo> {
  return api<Activo>(`/activos/${uuid}`);
}

export function createActivo(body: ActivoCreate): Promise<Activo> {
  return api<Activo>("/activos", { method: "POST", body: JSON.stringify(body) });
}

export function updateActivo(uuid: string, body: ActivoUpdate): Promise<Activo> {
  return api<Activo>(`/activos/${uuid}`, { method: "PATCH", body: JSON.stringify(body) });
}

export function transferirActivo(
  uuid: string,
  body: ActivoTransferirRequest,
): Promise<ActivoTransferirResponse> {
  return api<ActivoTransferirResponse>(`/activos/${uuid}/transferir`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
