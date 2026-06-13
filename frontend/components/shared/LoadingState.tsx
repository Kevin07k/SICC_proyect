export function LoadingState({ label = "Cargando..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-16">
      <p className="text-slate-400 animate-pulse">{label}</p>
    </div>
  );
}
