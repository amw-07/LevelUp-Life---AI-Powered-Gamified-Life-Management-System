import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { User, Trophy, Target, Edit2, Check, X, TrendingUp } from "lucide-react";
import { getMe, updateMe, getAchievements } from "../api/users";
import { ALL_STATS, STAT_COLORS, STAT_TEXT_COLORS } from "../utils/gameMechanics";
import type { Achievement } from "../types";

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [editingGoals, setEditingGoals] = useState(false);
  const [goals, setGoals] = useState<Record<string, string[]>>({
    fitness: [],
    productivity: [],
    learning: [],
  });
  const [tempGoals, setTempGoals] = useState<Record<string, string[]>>({
    fitness: [],
    productivity: [],
    learning: [],
  });

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["user"],
    queryFn: getMe,
  });

  const { data: achievements = [] } = useQuery({
    queryKey: ["achievements"],
    queryFn: getAchievements,
  });

  const updateMutation = useMutation({
    mutationFn: (data: { goals: Record<string, string[]> }) => updateMe(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      setEditingGoals(false);
    },
  });

  const handleEditGoals = () => {
    setTempGoals(user?.goals || { fitness: [], productivity: [], learning: [] });
    setEditingGoals(true);
  };

  const handleCancelEdit = () => {
    setEditingGoals(false);
    setTempGoals({ fitness: [], productivity: [], learning: [] });
  };

  const handleSaveGoals = () => {
    updateMutation.mutate({ goals: tempGoals });
  };

  const handleAddGoal = (domain: string) => {
    setTempGoals({
      ...tempGoals,
      [domain]: [...tempGoals[domain], ""],
    });
  };

  const handleGoalChange = (domain: string, index: number, value: string) => {
    const newGoals = [...tempGoals[domain]];
    newGoals[index] = value;
    setTempGoals({
      ...tempGoals,
      [domain]: newGoals,
    });
  };

  const handleRemoveGoal = (domain: string, index: number) => {
    const newGoals = tempGoals[domain].filter((_, i) => i !== index);
    setTempGoals({
      ...tempGoals,
      [domain]: newGoals,
    });
  };

  if (userLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">Loading your profile...</div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-3xl font-black text-white mb-6 flex items-center gap-3">
          <User className="text-purple-400" size={32} />
          Profile
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Section */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <h2 className="text-xl font-bold text-white mb-5 flex items-center gap-2">
                <TrendingUp className="text-purple-400" size={20} />
                Character Stats
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {ALL_STATS.map((stat) => {
                  const value = user.stats[stat] ?? 0;
                  return (
                    <div key={stat}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className={`capitalize ${STAT_TEXT_COLORS[stat]}`}>
                          {stat}
                        </span>
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

            {/* Achievements Section */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <h2 className="text-xl font-bold text-white mb-5 flex items-center gap-2">
                <Trophy className="text-yellow-400" size={20} />
                Achievements
                <span className="text-sm text-purple-300 font-normal">
                  ({achievements.length})
                </span>
              </h2>
              {achievements.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {achievements.map((achievement: Achievement) => (
                    <div
                      key={achievement.id}
                      className="bg-slate-700 rounded-lg p-4 text-center hover:bg-slate-600 transition-colors"
                    >
                      <div className="text-4xl mb-2">{achievement.icon}</div>
                      <h3 className="text-white font-semibold text-sm mb-1">
                        {achievement.name}
                      </h3>
                      <p className="text-gray-400 text-xs">
                        {achievement.description}
                      </p>
                      <p className="text-purple-300 text-xs mt-2">
                        {new Date(achievement.earned_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Trophy className="mx-auto mb-3 text-gray-500" size={48} />
                  <p>No achievements yet. Complete quests to earn them!</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* User Info Card */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <div className="text-center mb-4">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full mx-auto flex items-center justify-center text-white text-3xl font-black mb-3">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <h2 className="text-xl font-bold text-white">{user.username}</h2>
                <p className="text-gray-400 text-sm">{user.email}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="bg-slate-700 rounded-lg p-3">
                  <p className="text-2xl font-bold text-white">{user.level}</p>
                  <p className="text-gray-400 text-xs">Level</p>
                </div>
                <div className="bg-slate-700 rounded-lg p-3">
                  <p className="text-2xl font-bold text-yellow-400">{user.rank}</p>
                  <p className="text-gray-400 text-xs">Rank</p>
                </div>
              </div>
            </div>

            {/* Goals Section */}
            <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Target className="text-purple-400" size={18} />
                  Goals
                </h2>
                {!editingGoals && (
                  <button
                    onClick={handleEditGoals}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <Edit2 size={16} />
                  </button>
                )}
              </div>

              {editingGoals ? (
                <div className="space-y-4">
                  {(["fitness", "productivity", "learning"] as const).map((domain) => (
                    <div key={domain}>
                      <h3 className="text-sm font-semibold text-gray-300 capitalize mb-2">
                        {domain}
                      </h3>
                      <div className="space-y-2">
                        {tempGoals[domain].map((goal, index) => (
                          <div key={index} className="flex gap-2">
                            <input
                              type="text"
                              value={goal}
                              onChange={(e) => handleGoalChange(domain, index, e.target.value)}
                              className="flex-1 bg-slate-700 text-white text-sm px-3 py-2 rounded-lg border border-slate-600 focus:border-purple-500 focus:outline-none"
                              placeholder="Add a goal..."
                            />
                            <button
                              onClick={() => handleRemoveGoal(domain, index)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ))}
                        <button
                          onClick={() => handleAddGoal(domain)}
                          className="text-sm text-purple-400 hover:text-purple-300"
                        >
                          + Add goal
                        </button>
                      </div>
                    </div>
                  ))}
                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={handleSaveGoals}
                      disabled={updateMutation.isPending}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-1"
                    >
                      <Check size={16} />
                      Save
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="flex-1 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-1"
                    >
                      <X size={16} />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {(["fitness", "productivity", "learning"] as const).map((domain) => {
                    const domainGoals = user.goals?.[domain] || [];
                    return (
                      <div key={domain}>
                        <h3 className="text-sm font-semibold text-gray-300 capitalize mb-2">
                          {domain}
                        </h3>
                        {domainGoals.length > 0 ? (
                          <ul className="space-y-1">
                            {domainGoals.map((goal, index) => (
                              <li
                                key={index}
                                className="text-sm text-gray-400 flex items-start gap-2"
                              >
                                <span className="text-purple-400 mt-1">•</span>
                                <span>{goal}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-500 text-sm italic">No goals set</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Progress Summary */}
            <div className="bg-gradient-to-br from-purple-700 to-pink-700 rounded-xl p-6">
              <h2 className="text-lg font-bold text-white mb-3">Progress Summary</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-purple-100">
                  <span>Total XP</span>
                  <span className="font-bold">{user.total_xp.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-purple-100">
                  <span>Current Streak</span>
                  <span className="font-bold">{user.current_streak} days</span>
                </div>
                <div className="flex justify-between text-purple-100">
                  <span>Longest Streak</span>
                  <span className="font-bold">{user.longest_streak} days</span>
                </div>
                <div className="flex justify-between text-purple-100">
                  <span>Quests Completed</span>
                  <span className="font-bold">{user.total_quests_completed}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
