export type QuestDomain = "fitness" | "productivity" | "learning";
export type QuestDifficulty = "easy" | "medium" | "hard";
export type Rank = "E" | "D" | "C" | "B" | "A" | "S" | "SS";

export interface Quest {
  id: string;
  user_id: string;
  title: string;
  description: string;
  domain: QuestDomain;
  difficulty: QuestDifficulty;
  xp_reward: number;
  stat_rewards: Record<string, number>;
  estimated_duration: string | null;
  context_tags: string[];
  is_completed: boolean;
  completed_at: string | null;
  quest_date: string;
  ai_generated: boolean;
  created_at: string;
}

export interface Achievement {
  id: string;
  key: string;
  name: string;
  description: string;
  icon: string;
  earned_at: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  level: number;
  total_xp: number;
  rank: Rank;
  current_streak: number;
  longest_streak: number;
  stats: Record<string, number>;
  goals: Record<string, string[]>;
  mindset_profile: string[];
  work_style: string;
  activity_level: string;
  quests_by_domain: Record<string, number>;
  total_quests_completed: number;
  onboarding_completed: boolean;
  achievements: Achievement[];
  created_at: string;
}

export interface CompletionResult {
  xp_gained: number;
  new_total_xp: number;
  new_level: number;
  new_rank: Rank;
  leveled_up: boolean;
  ranked_up: boolean;
  streak_info: {
    current_streak: number;
    longest_streak: number;
    message: string;
  };
  new_achievements: Achievement[];
  updated_stats: Record<string, number>;
}

export interface QuestsResponse {
  quests: Quest[];
  generating: boolean;
  task_id: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type WsEventType =
  | "quest_generated"
  | "quest_completed"
  | "level_up"
  | "achievement_earned"
  | "streak_update"
  | "ping";

export interface WsEvent {
  type: WsEventType;
  payload: Record<string, unknown>;
}
