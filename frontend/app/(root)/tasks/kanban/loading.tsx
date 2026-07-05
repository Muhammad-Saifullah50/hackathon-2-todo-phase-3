export default function KanbanLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 shrink-0">
        <div className="h-9 w-48 bg-muted rounded animate-pulse" />
        <div className="h-4 w-64 bg-muted rounded mt-2 animate-pulse" />
      </div>
      <div className="flex-1 flex gap-4 overflow-x-auto pb-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex-1 min-w-[280px] bg-muted/30 rounded-xl p-4 space-y-3">
            <div className="h-6 w-24 bg-muted rounded animate-pulse" />
            {Array.from({ length: 3 }).map((_, j) => (
              <div key={j} className="h-28 bg-muted rounded-lg animate-pulse" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
