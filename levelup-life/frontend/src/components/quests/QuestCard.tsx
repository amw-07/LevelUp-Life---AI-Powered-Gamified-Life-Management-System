import { CheckCircle, Circle, Clock } from "lucide-react";
import type { Quest } from "../../types";
import {
  DOMAIN_BORDER_COLORS,
  DOMAIN_COLORS,
  DIFFICULTY_BADGE_COLORS,
} from "../../utils/gameMechanics";

interface QuestCardProps {
  quest: Quest;
  onComplete: (questId: string) => void;
  isCompleting: boolean;
}

export function QuestCard({ quest, onComplete, isCompleting }: QuestCardProps) {
  const borderColor = DOMAIN_BORDER_COLORS[quest.domain];
  const domainColor = DOMAIN_COLORS[quest.domain];
  const difficultyColor = DIFFICULTY_BADGE_COLORS[quest.difficulty];

  return (
    <div
      className={`bg-slate-700 rounded-xl p-4 border-l-4 ${borderColor} transition-all duration-300 ${
        quest.is_completed ? "opacity-50" : "hover:bg-slate-600"
      }`}
    >
      <div className="flex items-start gap-3">
        <button
          onClick={() => !quest.is_completed && onComplete(quest.id)}
          disabled={quest.is_completed || isCompleting}
          className="mt-1 flex-shrink-0 disabled:cursor-not-allowed"
          aria-label={quest.is_completed ? "Quest completed" : "Complete quest"}
        >
          {quest.is_completed ? (
            <CheckCircle className="text-green-400" size={24} />
          ) : (
            <Circle
              className={`${isCompleting ? "text-gray-500" : "text-gray-400 hover:text-purple-400"} transition-colors`}
              size={24}
            />
          )}
        </button>

        <div className="flex-1 min-w-0">
          <h3
            className={`font-semibold leading-snug ${
              quest.is_completed ? "text-gray-400 line-through" : "text-white"
            }`}
          >
            {quest.title}
          </h3>
          <p className="text-gray-400 text-sm mt-1 leading-relaxed">{quest.description}</p>

          <div className="flex items-center flex-wrap gap-2 mt-3">
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${domainColor} text-white`}>
              {quest.domain.toUpperCase()}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${difficultyColor}`}>
              {quest.difficulty.toUpperCase()}
            </span>
            {quest.estimated_duration && (
              <span className="flex items-center gap-1 text-gray-400 text-xs">
                <Clock size={11} />
                {quest.estimated_duration}
              </span>
            )}
            {quest.context_tags.slice(0, 2).map((tag) => (
              <span key={tag} className="text-gray-500 text-xs">
                #{tag}
              </span>
            ))}
          </div>
        </div>

        <div className="flex-shrink-0 text-right">
          <span className="text-yellow-400 font-bold text-sm whitespace-nowrap">
            +{quest.xp_reward} XP
          </span>
        </div>
      </div>
    </div>
  );
}
