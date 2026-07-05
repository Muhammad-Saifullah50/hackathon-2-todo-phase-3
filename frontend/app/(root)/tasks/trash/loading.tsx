export default function TrashLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 shrink-0">
        <div className="h-9 w-24 bg-muted rounded animate-pulse" />
        <div className="h-4 w-48 bg-muted rounded mt-2 animate-pulse" />
      </div>
      <div className="flex-1 space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  );
}
