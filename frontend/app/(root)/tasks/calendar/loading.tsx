export default function CalendarLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 shrink-0">
        <div className="h-9 w-36 bg-muted rounded animate-pulse" />
        <div className="h-4 w-64 bg-muted rounded mt-2 animate-pulse" />
      </div>
      <div className="flex-1 grid grid-cols-7 gap-px bg-muted rounded-lg overflow-hidden">
        {Array.from({ length: 35 }).map((_, i) => (
          <div key={i} className="bg-background p-2 min-h-[100px] animate-pulse" />
        ))}
      </div>
    </div>
  );
}
