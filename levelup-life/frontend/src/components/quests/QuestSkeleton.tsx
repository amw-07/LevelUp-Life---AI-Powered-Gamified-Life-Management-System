export function QuestSkeleton() {
  return (
    <div className="bg-slate-700 rounded-xl p-4 border-l-4 border-slate-600 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-6 h-6 rounded-full skeleton mt-1 flex-shrink-0" />
        <div className="flex-1">
          <div className="h-4 skeleton rounded w-3/4 mb-2" />
          <div className="h-3 skeleton rounded w-full mb-1" />
          <div className="h-3 skeleton rounded w-2/3" />
          <div className="flex gap-2 mt-3">
            <div className="h-5 w-16 skeleton rounded" />
            <div className="h-5 w-14 skeleton rounded" />
            <div className="h-5 w-12 skeleton rounded" />
          </div>
        </div>
        <div className="h-5 w-16 skeleton rounded" />
      </div>
    </div>
  );
}
