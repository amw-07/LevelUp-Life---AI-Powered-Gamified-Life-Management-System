import api from "./client";
import type { User, Achievement } from "../types";

export async function getMe(): Promise<User> {
  const res = await api.get<User>("/users/me");
  return res.data;
}

export async function getAchievements(): Promise<Achievement[]> {
  const res = await api.get<Achievement[]>("/users/me/achievements");
  return res.data;
}

export async function completeOnboarding(data: {
  goals: Record<string, string[]>;
  mindset_profile: string[];
  work_style: string;
  activity_level: string;
  preferred_times: Record<string, string>;
}): Promise<User> {
  const res = await api.post<User>("/users/me/onboarding", data);
  return res.data;
}
