import { Flame, Trophy, Zap } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getMe } from "../api/users";
import { RANK_COLORS, RANK_BORDER_COLORS } from "../utils/gameMechanics";
import type { Rank } from "../types";

interface TopBarProps {
  username?: string;
  currentStreak?: number;
  rank?: Rank;
  totalXp?: number;
}

export default function TopBar({ username, currentStreak, rank, totalXp }: TopBarProps) {
  // If props are provided, use them; otherwise fetch user data
  const { data: user } = useQuery({
    queryKey: ["user"],
    queryFn: getMe,
    enabled: !username && !currentStreak && !rank,
  });

  const displayUsername = username || user?.username;
  const displayStreak = currentStreak ?? user?.current_streak;
  const displayRank = rank || user?.rank;
  const displayXp = totalXp ?? user?.total_xp;

  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-6">
        {/* Username */}
        <div className="flex items-center gap-3">
          <span className="text-white font-semibold text-lg">{displayUsername}</span>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-slate-600" />

        {/* Streak */}
        <div className="flex items-center gap-2">
          <div className="bg-orange-500/20 p-1.5 rounded-lg">
            <Flame className="text-orange-400" size={18} />
          </div>
          <div className="flex flex-col">
            <span className="text-white font-bold text-lg">{displayStreak}</span>
            <span className="text-gray-400 text-xs">Day Streak</span>
          </div>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-slate-600" />

        {/* Rank Badge */}
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 ${RANK_BORDER_COLORS[displayRank || "E"]} bg-slate-700`}
        >
          <Trophy className={`w-5 h-5 ${RANK_COLORS[displayRank || "E"]}`} />
          <div className="flex flex-col">
            <span className={`font-black text-xl ${RANK_COLORS[displayRank || "E"]}`}>
              {displayRank}
            </span>
            <span className="text-gray-400 text-xs">Rank</span>
          </div>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-slate-600" />

        {/* XP */}
        <div className="flex items-center gap-2">
          <div className="bg-yellow-500/20 p-1.5 rounded-lg">
            <Zap className="text-yellow-400" size={18} />
          </div>
          <div className="flex flex-col">
            <span className="text-white font-bold text-lg">
              {displayXp?.toLocaleString()}
            </span>
            <span className="text-gray-400 text-xs">Total XP</span>
          </div>
        </div>
      </div>

      {/* Right side - can add notifications or settings here */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-gray-400 text-sm">Today's Progress</p>
          <p className="text-white font-semibold">Keep pushing!</p>
        </div>
      </div>
    </header>
  );
}
