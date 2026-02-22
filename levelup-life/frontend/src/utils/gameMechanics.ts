import type { Rank, QuestDomain, QuestDifficulty } from "../types";

export const RANK_THRESHOLDS: Record<Rank, number> = {
  E: 0,
  D: 1000,
  C: 5000,
  B: 15000,
  A: 35000,
  S: 70000,
  SS: 150000,
};

export const RANKS: Rank[] = ["E", "D", "C", "B", "A", "S", "SS"];

export function getRankFromXp(xp: number): Rank {
  let current: Rank = "E";
  for (const rank of RANKS) {
    if (xp >= RANK_THRESHOLDS[rank]) current = rank;
  }
  return current;
}

export function getLevelFromXp(xp: number): number {
  return Math.max(1, Math.floor(xp / 500) + 1);
}

export function getRankProgress(xp: number): {
  percent: number;
  xpNeeded: number;
  nextRank: Rank | null;
} {
  const current = getRankFromXp(xp);
  const idx = RANKS.indexOf(current);
  if (idx === RANKS.length - 1) {
    return { percent: 100, xpNeeded: 0, nextRank: null };
  }
  const nextRank = RANKS[idx + 1];
  const lower = RANK_THRESHOLDS[current];
  const upper = RANK_THRESHOLDS[nextRank];
  const percent = ((xp - lower) / (upper - lower)) * 100;
  return { percent: Math.min(100, Math.max(0, percent)), xpNeeded: upper - xp, nextRank };
}

export const RANK_COLORS: Record<Rank, string> = {
  E: "text-gray-400",
  D: "text-green-400",
  C: "text-blue-400",
  B: "text-purple-400",
  A: "text-yellow-400",
  S: "text-orange-400",
  SS: "text-red-400",
};

export const RANK_BORDER_COLORS: Record<Rank, string> = {
  E: "border-gray-400",
  D: "border-green-400",
  C: "border-blue-400",
  B: "border-purple-400",
  A: "border-yellow-400",
  S: "border-orange-400",
  SS: "border-red-400",
};

export const DOMAIN_COLORS: Record<QuestDomain, string> = {
  fitness: "bg-red-500",
  productivity: "bg-blue-500",
  learning: "bg-purple-500",
};

export const DOMAIN_BORDER_COLORS: Record<QuestDomain, string> = {
  fitness: "border-red-500",
  productivity: "border-blue-500",
  learning: "border-purple-500",
};

export const DOMAIN_TEXT_COLORS: Record<QuestDomain, string> = {
  fitness: "text-red-400",
  productivity: "text-blue-400",
  learning: "text-purple-400",
};

export const DIFFICULTY_BADGE_COLORS: Record<QuestDifficulty, string> = {
  easy: "bg-green-900 text-green-300",
  medium: "bg-yellow-900 text-yellow-300",
  hard: "bg-red-900 text-red-300",
};

export const STAT_COLORS: Record<string, string> = {
  strength: "bg-red-500",
  vitality: "bg-green-500",
  endurance: "bg-orange-500",
  focus: "bg-blue-500",
  efficiency: "bg-cyan-500",
  execution: "bg-teal-500",
  intelligence: "bg-purple-500",
  creativity: "bg-pink-500",
  wisdom: "bg-yellow-500",
};

export const STAT_TEXT_COLORS: Record<string, string> = {
  strength: "text-red-300",
  vitality: "text-green-300",
  endurance: "text-orange-300",
  focus: "text-blue-300",
  efficiency: "text-cyan-300",
  execution: "text-teal-300",
  intelligence: "text-purple-300",
  creativity: "text-pink-300",
  wisdom: "text-yellow-300",
};

export const ALL_STATS = [
  "strength",
  "vitality",
  "endurance",
  "focus",
  "efficiency",
  "execution",
  "intelligence",
  "creativity",
  "wisdom",
] as const;

export function getXpForNextLevel(xp: number): number {
  const level = getLevelFromXp(xp);
  return level * 500;
}

export function getLevelProgress(xp: number): number {
  const level = getLevelFromXp(xp);
  const levelStart = (level - 1) * 500;
  const levelEnd = level * 500;
  return ((xp - levelStart) / (levelEnd - levelStart)) * 100;
}
