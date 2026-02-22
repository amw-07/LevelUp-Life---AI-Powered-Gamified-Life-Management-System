import api from "./client";
import type { Quest, QuestsResponse, CompletionResult } from "../types";

export async function getTodayQuests(): Promise<QuestsResponse> {
  const res = await api.get<QuestsResponse>("/quests/today");
  return res.data;
}

export async function generateQuests(): Promise<{ task_id: string }> {
  const res = await api.post<{ task_id: string }>("/quests/generate");
  return res.data;
}

export async function completeQuest(questId: string): Promise<CompletionResult> {
  const res = await api.post<CompletionResult>(`/quests/${questId}/complete`);
  return res.data;
}

export async function getQuestHistory(days = 30): Promise<Quest[]> {
  const res = await api.get<Quest[]>(`/quests/history?days=${days}`);
  return res.data;
}
