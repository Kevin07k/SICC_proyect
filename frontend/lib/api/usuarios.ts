import { api } from "@/lib/api/client";
import type { Usuario, UsuarioCreate, UsuarioUpdate } from "@/types/usuarios";

export function listUsuarios(): Promise<Usuario[]> {
  return api<Usuario[]>("/usuarios");
}

export function getUsuario(uuid: string): Promise<Usuario> {
  return api<Usuario>(`/usuarios/${uuid}`);
}

export function createUsuario(body: UsuarioCreate): Promise<Usuario> {
  return api<Usuario>("/usuarios", { method: "POST", body: JSON.stringify(body) });
}

export function updateUsuario(uuid: string, body: UsuarioUpdate): Promise<Usuario> {
  return api<Usuario>(`/usuarios/${uuid}`, { method: "PATCH", body: JSON.stringify(body) });
}
