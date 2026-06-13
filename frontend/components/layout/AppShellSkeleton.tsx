export function AppShellSkeleton({ title }: { title: string }) {
  return (
    <div className="flex min-h-screen bg-slate-950">
      <aside className="w-64 border-r border-slate-800 bg-slate-900/90 p-4" aria-hidden>
        <div className="mb-8 h-10 rounded-lg bg-slate-800/60" />
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-9 rounded-lg bg-slate-800/40" />
          ))}
        </div>
      </aside>
      <main className="flex-1 p-8">
        <div className="mb-8 h-14 rounded-xl border border-slate-800 bg-slate-900/60" />
        <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <p className="sr-only">{title}</p>
          <div className="h-32 animate-pulse rounded-lg bg-slate-800/40" />
        </section>
      </main>
    </div>
  );
}
