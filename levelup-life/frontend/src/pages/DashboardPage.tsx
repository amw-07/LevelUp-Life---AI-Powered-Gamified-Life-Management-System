import { useState, useCallback, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Zap, Trophy, Flame, Target, TrendingUp, Star, LogOut } from "lucide-react";
import { getMe } from "../api/users";
import { getTodayQuests, completeQuest, generateQuests } from "../api/quests";
import { useAuthStore } from "../store/authStore";
import { useWebSocket } from "../hooks/useWebSocket";
import { QuestList } from "../components/quests/QuestList";
import { XpRollUp } from "../components/animations/XpRollUp";
import { LevelUpOverlay } from "../components/animations/LevelUpOverlay";
import { AchievementToastContainer } from "../components/animations/AchievementToast";
import {
  getRankProgress,
  RANK_COLORS,
  STAT_COLORS,
  STAT_TEXT_COLORS,
  ALL_STATS,
  getLevelProgress,
} from "../utils/gameMechanics";
import type { Achievement, CompletionResult, Rank, WsEvent } from "../types";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const clearTokens = useAuthStore((s) => s.clearTokens);

  const [xpAnimation, setXpAnimation] = useState<number | null>(null);
  const [levelUpData, setLevelUpData] = useState<{ level: number; rank: Rank; rankedUp: boolean } | null>(null);
  const [pendingAchievements, setPendingAchievements] = useState<Achievement[]>([]);
  const [completingId, setCompletingId] = useState<string | null>(null);
  const achievementQueue = useRef<Achievement[]>([]);

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["user"],
    queryFn: getMe,
  });

  const { data: questsData, isLoading: questsLoading } = useQuery({
    queryKey: ["quests-today"],
    queryFn: getTodayQuests,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.generating && (data?.quests?.length ?? 0) === 0 ? 3000 : false;
    },
  });

  const generateMutation = useMutation({
    mutationFn: generateQuests,
    onSuccess: () => {
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ["quests-today"] }), 2000);
    },
  });

  const completeMutation = useMutation({
    mutationFn: completeQuest,
    onSuccess: (result: CompletionResult) => {
      setCompletingId(null);
      queryClient.invalidateQueries({ queryKey: ["quests-today"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });

      setXpAnimation(result.xp_gained);

      if (result.leveled_up) {
        setLevelUpData({
          level: result.new_level,
          rank: result.new_rank,
          rankedUp: result.ranked_up,
        });
      }

      if (result.new_achievements.length > 0) {
        achievementQueue.current = [...achievementQueue.current, ...result.new_achievements];
        if (pendingAchievements.length === 0) {
          showNextAchievement();
        }
      }
    },
    onError: () => {
      setCompletingId(null);
    },
  });

  const showNextAchievement = useCallback(() => {
    if (achievementQueue.current.length === 0) {
      setPendingAchievements([]);
      return;
    }
    const next = achievementQueue.current.shift()!;
    setPendingAchievements([next]);
  }, [pendingAchievements.length]);

  const handleDismissAchievement = useCallback(
    (_id: string) => {
      showNextAchievement();
    },
    [showNextAchievement]
  );

  const handleWsEvent = useCallback(
    (event: WsEvent) => {
      if (event.type === "quest_generated") {
        queryClient.invalidateQueries({ queryKey: ["quests-today"] });
      } else if (event.type === "achievement_earned") {
        queryClient.invalidateQueries({ queryKey: ["user"] });
      }
    },
    [queryClient]
  );

  useWebSocket({
    userId: user?.id ?? null,
    onEvent: handleWsEvent,
  });

  const handleCompleteQuest = useCallback(
    (questId: string) => {
      setCompletingId(questId);
      completeMutation.mutate(questId);
    },
    [completeMutation]
  );

  const handleLogout = useCallback(() => {
    clearTokens();
  }, [clearTokens]);

  if (userLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">Loading your adventure…</div>
      </div>
    );
  }

  if (!user) return null;

  const rankProgress = getRankProgress(user.total_xp);
  const levelPct = getLevelProgress(user.total_xp);
  const quests = questsData?.quests ?? [];
  const todayCompleted = quests.filter((q) => q.is_completed).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* XP Roll-up Animation */}
      {xpAnimation !== null && (
        <XpRollUp xpGained={xpAnimation} onComplete={() => setXpAnimation(null)} />
      )}

      {/* Level-up Overlay */}
      {levelUpData && (
        <LevelUpOverlay
          newLevel={levelUpData.level}
          newRank={levelUpData.rank}
          rankedUp={levelUpData.rankedUp}
          onClose={() => setLevelUpData(null)}
        />
      )}

      {/* Achievement Toasts */}
      <AchievementToastContainer
        achievements={pendingAchievements}
        onDismiss={handleDismissAchievement}
      />

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Section 1: Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-black text-white">⚔️ LevelUp Life</h1>
            <p className="text-purple-300 text-sm mt-1">Welcome back, {user.username}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>

        {/* Section 2: Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800 rounded-xl p-5 border border-purple-500/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Level</span>
              <Zap className="text-yellow-400" size={18} />
            </div>
            <div className="text-4xl font-black text-white">{user.level}</div>
            <div className="text-xs text-purple-300 mt-1">{user.total_xp.toLocaleString()} XP</div>
            <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
              <div
                className="bg-yellow-400 h-1.5 rounded-full transition-all duration-700"
                style={{ width: `${levelPct}%` }}
              />
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-5 border border-purple-500/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Rank</span>
              <Trophy className="text-yellow-400" size={18} />
            </div>
            <div className={`text-4xl font-black ${RANK_COLORS[user.rank]}`}>{user.rank}</div>
            <div className="text-xs text-purple-300 mt-1">
              {rankProgress.nextRank
                ? `${rankProgress.xpNeeded.toLocaleString()} XP to ${rankProgress.nextRank}`
                : "MAX RANK"}
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-5 border border-purple-500/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Streak</span>
              <Flame className="text-orange-400" size={18} />
            </div>
            <div className="text-4xl font-black text-white">{user.current_streak}</div>
            <div className="text-xs text-purple-300 mt-1">🏆 Best: {user.longest_streak}</div>
          </div>

          <div className="bg-slate-800 rounded-xl p-5 border border-purple-500/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Today</span>
              <Target className="text-green-400" size={18} />
            </div>
            <div className="text-4xl font-black text-white">
              {todayCompleted}/{quests.length}
            </div>
            <div className="text-xs text-purple-300 mt-1">Quests Done</div>
          </div>
        </div>

        {/* Section 3: Rank Progress Bar */}
        <div className="bg-slate-800 rounded-xl p-5 border border-purple-500/50 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-white font-semibold">Rank Progress</span>
            <span className="text-purple-300 text-sm">{Math.round(rankProgress.percent)}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-700"
              style={{ width: `${rankProgress.percent}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm">
            <span className={`font-bold ${RANK_COLORS[user.rank]}`}>{user.rank}</span>
            {rankProgress.nextRank && (
              <span className={`font-bold ${RANK_COLORS[rankProgress.nextRank]}`}>
                {rankProgress.nextRank}
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Section 4: Quest List (main area) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Motivational quote */}
            <div className="bg-gradient-to-r from-purple-700 to-pink-700 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <Star className="text-yellow-300 flex-shrink-0 mt-0.5" size={22} />
                <div>
                  <p className="text-white italic leading-relaxed">
                    "The body achieves what the mind believes."
                  </p>
                  <p className="text-purple-200 text-xs mt-2">— Your AI Coach</p>
                </div>
              </div>
            </div>

            {/* Daily Quests */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <h2 className="text-xl font-bold text-white mb-5 flex items-center gap-2">
                <Target size={20} className="text-purple-400" />
                Daily Quests
              </h2>
              <QuestList
                quests={quests}
                generating={questsData?.generating ?? false}
                isLoading={questsLoading}
                completingId={completingId}
                onComplete={handleCompleteQuest}
                onGenerate={() => generateMutation.mutate()}
                isGenerating={generateMutation.isPending}
              />
            </div>
          </div>

          {/* Section 5: Stats Sidebar */}
          <div className="space-y-6">
            {/* Character Stats */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <h3 className="text-lg font-bold text-white mb-5 flex items-center gap-2">
                <TrendingUp size={18} className="text-purple-400" />
                Character Stats
              </h3>
              <div className="space-y-3">
                {ALL_STATS.map((stat) => {
                  const value = user.stats[stat] ?? 0;
                  return (
                    <div key={stat}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className={`capitalize ${STAT_TEXT_COLORS[stat]}`}>{stat}</span>
                        <span className="text-white font-semibold">{value}</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div
                          className={`${STAT_COLORS[stat]} h-2 rounded-full transition-all duration-700`}
                          style={{ width: `${Math.min(100, value)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Quest Domain Breakdown */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <h3 className="text-lg font-bold text-white mb-4">Domain Progress</h3>
              <div className="space-y-2">
                {(["fitness", "productivity", "learning"] as const).map((domain) => (
                  <div key={domain} className="flex justify-between items-center text-sm">
                    <span className="text-gray-400 capitalize">{domain}</span>
                    <span className="text-white font-semibold">
                      {user.quests_by_domain[domain] ?? 0} quests
                    </span>
                  </div>
                ))}
                <div className="pt-2 border-t border-slate-700 flex justify-between text-sm">
                  <span className="text-gray-400">Total Completed</span>
                  <span className="text-yellow-400 font-bold">{user.total_quests_completed}</span>
                </div>
              </div>
            </div>

            {/* Achievements */}
            {user.achievements.length > 0 && (
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
                <h3 className="text-lg font-bold text-white mb-4">Achievements</h3>
                <div className="flex flex-wrap gap-3">
                  {user.achievements.slice(0, 8).map((ach) => (
                    <div
                      key={ach.id}
                      title={ach.name}
                      className="w-10 h-10 flex items-center justify-center bg-slate-700 rounded-lg text-xl"
                    >
                      {ach.icon}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Status */}
            <div className="bg-gradient-to-br from-purple-700 to-pink-700 rounded-xl p-5">
              <h3 className="text-base font-bold text-white mb-2">🤖 AI Agents Active</h3>
              <p className="text-purple-200 text-sm">
                5 specialized agents optimizing your quest experience in real-time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
