import { RefreshCw, Loader2 } from "lucide-react";
import { QuestCard } from "./QuestCard";
import { QuestSkeleton } from "./QuestSkeleton";
import type { Quest } from "../../types";

interface QuestListProps {
  quests: Quest[];
  generating: boolean;
  isLoading: boolean;
  completingId: string | null;
  onComplete: (questId: string) => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

export function QuestList({
  quests,
  generating,
  isLoading,
  completingId,
  onComplete,
  onGenerate,
  isGenerating,
}: QuestListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <QuestSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (generating && quests.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Loader2 className="text-purple-400 animate-spin mb-4" size={40} />
        <p className="text-white font-semibold text-lg">Generating your quests…</p>
        <p className="text-gray-400 text-sm mt-2">AI agents are crafting your personalized challenges</p>
      </div>
    );
  }

  if (quests.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-gray-400 text-lg mb-4">No quests for today yet.</p>
        <button
          onClick={onGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
        >
          {isGenerating ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <RefreshCw size={18} />
          )}
          Generate Quests
        </button>
      </div>
    );
  }

  const completed = quests.filter((q) => q.is_completed).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-gray-400 text-sm">
          {completed}/{quests.length} completed
        </p>
        <button
          onClick={onGenerate}
          disabled={isGenerating}
          className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          {isGenerating ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <RefreshCw size={14} />
          )}
          Regenerate
        </button>
      </div>

      <div className="space-y-3">
        {quests.map((quest) => (
          <QuestCard
            key={quest.id}
            quest={quest}
            onComplete={onComplete}
            isCompleting={completingId === quest.id}
          />
        ))}
      </div>
    </div>
  );
}
