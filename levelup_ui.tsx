import React, { useState } from 'react';
import { Trophy, Target, Flame, TrendingUp, Star, CheckCircle, Circle, Clock, Zap } from 'lucide-react';

const LevelUpLifeDashboard = () => {
  // Demo user state
  const [user, setUser] = useState({
    name: "Alex",
    level: 5,
    totalXP: 2500,
    rank: 'D',
    currentStreak: 7,
    longestStreak: 14,
    stats: {
      strength: 25,
      vitality: 20,
      endurance: 22,
      focus: 30,
      efficiency: 28,
      execution: 26,
      intelligence: 35,
      creativity: 32,
      wisdom: 30
    }
  });

  // Demo quests
  const [quests, setQuests] = useState([
    {
      id: 1,
      title: "30-Minute Morning Workout",
      description: "Complete a full-body workout routine focusing on strength and endurance",
      domain: "fitness",
      difficulty: "medium",
      xpReward: 100,
      duration: "30 min",
      completed: false
    },
    {
      id: 2,
      title: "Deep Work Session: Project Milestone",
      description: "Complete 90 minutes of focused work on your priority project",
      domain: "productivity",
      difficulty: "medium",
      xpReward: 90,
      duration: "90 min",
      completed: false
    },
    {
      id: 3,
      title: "AI Course: Neural Networks Module",
      description: "Watch lectures and complete exercises on neural network fundamentals",
      domain: "learning",
      difficulty: "hard",
      xpReward: 180,
      duration: "120 min",
      completed: false
    },
    {
      id: 4,
      title: "Plan Tomorrow's Top 3 Tasks",
      description: "Review priorities and plan your three most important tasks",
      domain: "productivity",
      difficulty: "easy",
      xpReward: 40,
      duration: "10 min",
      completed: false
    },
    {
      id: 5,
      title: "Read 15 Pages of Educational Book",
      description: "Continue reading your current educational book and take notes",
      domain: "learning",
      difficulty: "easy",
      xpReward: 60,
      duration: "20 min",
      completed: false
    }
  ]);

  const [motivationalQuote, setMotivationalQuote] = useState(
    "The body achieves what the mind believes."
  );
  const [showCelebration, setShowCelebration] = useState(false);

  // Domain colors
  const domainColors = {
    fitness: 'bg-red-500',
    productivity: 'bg-blue-500',
    learning: 'bg-purple-500'
  };

  const domainBorders = {
    fitness: 'border-red-500',
    productivity: 'border-blue-500',
    learning: 'border-purple-500'
  };

  // Difficulty badges
  const difficultyColors = {
    easy: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    hard: 'bg-red-100 text-red-800'
  };

  // Rank colors
  const rankColors = {
    'E': 'text-gray-500',
    'D': 'text-green-500',
    'C': 'text-blue-500',
    'B': 'text-purple-500',
    'A': 'text-yellow-500',
    'S': 'text-orange-500',
    'SS': 'text-red-500'
  };

  // XP to next rank
  const rankThresholds = { E: 0, D: 1000, C: 5000, B: 15000, A: 35000, S: 70000, SS: 150000 };
  const nextRank = user.rank === 'E' ? 'D' : user.rank === 'D' ? 'C' : user.rank === 'C' ? 'B' : user.rank === 'B' ? 'A' : user.rank === 'A' ? 'S' : user.rank === 'S' ? 'SS' : 'MAX';
  const xpToNextRank = nextRank !== 'MAX' ? rankThresholds[nextRank] - user.totalXP : 0;
  const progressPercentage = nextRank !== 'MAX' ? ((user.totalXP - rankThresholds[user.rank]) / (rankThresholds[nextRank] - rankThresholds[user.rank])) * 100 : 100;

  // Complete quest
  const completeQuest = (questId) => {
    const quest = quests.find(q => q.id === questId);
    if (quest && !quest.completed) {
      // Update quest
      setQuests(quests.map(q => 
        q.id === questId ? { ...q, completed: true } : q
      ));
      
      // Update user XP
      setUser(prev => ({
        ...prev,
        totalXP: prev.totalXP + quest.xpReward
      }));

      // Show celebration
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 3000);

      // Update motivational quote based on domain
      const quotes = {
        fitness: "Consistency is the key to unlocking your potential.",
        productivity: "Focus on being productive instead of busy.",
        learning: "Learning is a treasure that follows its owner everywhere."
      };
      setMotivationalQuote(quotes[quest.domain] || "Progress, not perfection, is what we should be asking for.");
    }
  };

  const completedQuests = quests.filter(q => q.completed).length;
  const totalQuests = quests.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            ⚔️ LevelUp Life
          </h1>
          <p className="text-purple-300">AI-Powered Life Management System</p>
        </div>

        {/* Celebration Banner */}
        {showCelebration && (
          <div className="mb-6 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg p-4 animate-pulse">
            <p className="text-white text-center text-xl font-bold">
              🎉 Quest Complete! +XP Earned! 🎉
            </p>
          </div>
        )}

        {/* Top Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {/* Level Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">LEVEL</span>
              <Zap className="text-yellow-400" size={20} />
            </div>
            <div className="text-4xl font-bold text-white">{user.level}</div>
            <div className="text-sm text-purple-300 mt-1">{user.totalXP} Total XP</div>
          </div>

          {/* Rank Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">RANK</span>
              <Trophy className="text-yellow-400" size={20} />
            </div>
            <div className={`text-4xl font-bold ${rankColors[user.rank]}`}>{user.rank}</div>
            <div className="text-sm text-purple-300 mt-1">
              {xpToNextRank > 0 ? `${xpToNextRank} XP to ${nextRank}` : 'MAX RANK'}
            </div>
          </div>

          {/* Streak Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">STREAK</span>
              <Flame className="text-orange-400" size={20} />
            </div>
            <div className="text-4xl font-bold text-white">{user.currentStreak}</div>
            <div className="text-sm text-purple-300 mt-1">🔥 {user.longestStreak} Best</div>
          </div>

          {/* Quests Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">TODAY</span>
              <Target className="text-green-400" size={20} />
            </div>
            <div className="text-4xl font-bold text-white">{completedQuests}/{totalQuests}</div>
            <div className="text-sm text-purple-300 mt-1">Quests Done</div>
          </div>
        </div>

        {/* Rank Progress Bar */}
        <div className="bg-slate-800 rounded-lg p-6 border border-purple-500 mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-white font-semibold">Rank Progress</span>
            <span className="text-purple-300">{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-4">
            <div 
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm">
            <span className={`font-bold ${rankColors[user.rank]}`}>{user.rank}</span>
            {nextRank !== 'MAX' && (
              <span className={`font-bold ${rankColors[nextRank]}`}>{nextRank}</span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Quest Section */}
          <div className="lg:col-span-2">
            {/* Motivational Quote */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <Star className="text-yellow-300 mt-1 mr-3 flex-shrink-0" size={24} />
                <div>
                  <p className="text-white text-lg italic">"{motivationalQuote}"</p>
                  <p className="text-purple-200 text-sm mt-2">— Your AI Coach</p>
                </div>
              </div>
            </div>

            {/* Daily Quests */}
            <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                <Target className="mr-2" /> Daily Quests
              </h2>
              
              <div className="space-y-4">
                {quests.map(quest => (
                  <div 
                    key={quest.id}
                    className={`bg-slate-700 rounded-lg p-4 border-l-4 ${domainBorders[quest.domain]} transition-all ${quest.completed ? 'opacity-50' : 'hover:bg-slate-600'}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-start flex-1">
                        <button
                          onClick={() => completeQuest(quest.id)}
                          className="mt-1 mr-3 flex-shrink-0"
                          disabled={quest.completed}
                        >
                          {quest.completed ? (
                            <CheckCircle className="text-green-400" size={24} />
                          ) : (
                            <Circle className="text-gray-400 hover:text-purple-400" size={24} />
                          )}
                        </button>
                        <div className="flex-1">
                          <h3 className={`font-semibold ${quest.completed ? 'text-gray-400 line-through' : 'text-white'}`}>
                            {quest.title}
                          </h3>
                          <p className="text-gray-400 text-sm mt-1">{quest.description}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-3 ml-9">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${domainColors[quest.domain]} text-white`}>
                          {quest.domain.toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${difficultyColors[quest.difficulty]}`}>
                          {quest.difficulty.toUpperCase()}
                        </span>
                        <span className="text-gray-400 text-xs flex items-center">
                          <Clock size={12} className="mr-1" />
                          {quest.duration}
                        </span>
                      </div>
                      <span className="text-yellow-400 font-bold">+{quest.xpReward} XP</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Stats Sidebar */}
          <div className="space-y-6">
            {/* User Profile */}
            <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
              <h3 className="text-xl font-bold text-white mb-4">⚔️ {user.name}</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-red-300">Strength</span>
                    <span className="text-white font-semibold">{user.stats.strength}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: `${user.stats.strength}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-green-300">Vitality</span>
                    <span className="text-white font-semibold">{user.stats.vitality}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: `${user.stats.vitality}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-orange-300">Endurance</span>
                    <span className="text-white font-semibold">{user.stats.endurance}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-orange-500 h-2 rounded-full" style={{ width: `${user.stats.endurance}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-blue-300">Focus</span>
                    <span className="text-white font-semibold">{user.stats.focus}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${user.stats.focus}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-cyan-300">Efficiency</span>
                    <span className="text-white font-semibold">{user.stats.efficiency}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-cyan-500 h-2 rounded-full" style={{ width: `${user.stats.efficiency}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-purple-300">Intelligence</span>
                    <span className="text-white font-semibold">{user.stats.intelligence}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${user.stats.intelligence}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-pink-300">Creativity</span>
                    <span className="text-white font-semibold">{user.stats.creativity}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-pink-500 h-2 rounded-full" style={{ width: `${user.stats.creativity}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-yellow-300">Wisdom</span>
                    <span className="text-white font-semibold">{user.stats.wisdom}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${user.stats.wisdom}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-slate-800 rounded-lg p-6 border border-purple-500">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <TrendingUp className="mr-2" size={20} />
                Quick Stats
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Completion Rate</span>
                  <span className="text-white font-semibold">{Math.round((completedQuests/totalQuests)*100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Active Quests</span>
                  <span className="text-white font-semibold">{totalQuests - completedQuests}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Completed Today</span>
                  <span className="text-white font-semibold">{completedQuests}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total XP Earned</span>
                  <span className="text-yellow-400 font-semibold">{user.totalXP}</span>
                </div>
              </div>
            </div>

            {/* System Info */}
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-2">🤖 AI System Active</h3>
              <p className="text-purple-100 text-sm">
                5 agents monitoring your progress and optimizing your quest experience in real-time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LevelUpLifeDashboard;