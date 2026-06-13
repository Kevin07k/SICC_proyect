import { ShieldOff } from "lucide-react";

export function AccessDenied({ message = "No tienes permiso para ver esta sección." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <ShieldOff className="mb-4 h-12 w-12 text-slate-500" />
      <h2 className="text-xl font-semibold text-slate-200">Acceso denegado</h2>
      <p className="mt-2 max-w-md text-slate-400">{message}</p>
    </div>
  );
}
