import api from "./client";

export interface SummaryData {
  this_week: {
    quests_completed: number;
    xp_earned: number;
  };
  all_time: {
    quests_completed: number;
    xp_earned: number;
  };
  domain_distribution: Record<string, number>;
}

export interface WeeklyReportData {
  week: string;
  week_start: string;
  week_end: string;
  metrics: Record<string, { completed: number; xp: number }>;
  insights: string;
}

export interface StreakDataPoint {
  date: string;
  completed_count: number;
}

export interface PatternsData {
  best_day: string | null;
  best_time: string | null;
  top_domain: string | null;
  completion_rate_trend: number | null;
}

export const getSummary = async () => {
  const { data } = await api.get<SummaryData>("/analytics/summary");
  return data;
};

export const getWeeklyReport = async (week?: string) => {
  const params = week ? { week } : {};
  const { data } = await api.get<WeeklyReportData>("/analytics/weekly-report", { params });
  return data;
};

export const getStreaks = async () => {
  const { data } = await api.get<StreakDataPoint[]>("/analytics/streaks");
  return data;
};

export const getPatterns = async () => {
  const { data } = await api.get<PatternsData>("/analytics/patterns");
  return data;
};
