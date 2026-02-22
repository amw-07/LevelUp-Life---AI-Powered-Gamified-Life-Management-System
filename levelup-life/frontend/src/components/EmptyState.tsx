import { Target, Calendar, UserPlus, RefreshCw } from "lucide-react";

interface EmptyStateProps {
  type: "quests" | "history" | "newUser";
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ type, action }: EmptyStateProps) {
  const configs = {
    quests: {
      icon: Target,
      title: "No quests today",
      description: "Generate your daily quests to start your adventure!",
      color: "text-purple-400",
    },
    history: {
      icon: Calendar,
      title: "No history yet",
      description: "Complete quests to build your adventure history.",
      color: "text-blue-400",
    },
    newUser: {
      icon: UserPlus,
      title: "Welcome, adventurer!",
      description: "Complete onboarding to start your journey.",
      color: "text-green-400",
    },
  };

  const config = configs[type];
  const Icon = config.icon;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className={`bg-slate-700/50 p-6 rounded-full mb-4`}>
        <Icon className={config.color} size={48} />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{config.title}</h3>
      <p className="text-gray-400 text-center mb-6 max-w-sm">{config.description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
        >
          <RefreshCw size={18} />
          {action.label}
        </button>
      )}
    </div>
  );
}
