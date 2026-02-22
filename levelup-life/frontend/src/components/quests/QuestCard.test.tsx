import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QuestCard } from "./QuestCard";
import type { Quest } from "../../types";

const baseQuest: Quest = {
  id: "quest-1",
  user_id: "user-1",
  title: "Morning Run",
  description: "Run 5km before breakfast",
  domain: "fitness",
  difficulty: "medium",
  xp_reward: 150,
  stat_rewards: { strength: 2 },
  estimated_duration: "30 min",
  context_tags: ["running", "cardio"],
  is_completed: false,
  completed_at: null,
  quest_date: "2025-01-01",
  ai_generated: true,
  created_at: "2025-01-01T08:00:00Z",
};

describe("QuestCard", () => {
  it("renders quest title and description", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("Morning Run")).toBeInTheDocument();
    expect(screen.getByText("Run 5km before breakfast")).toBeInTheDocument();
  });

  it("displays xp reward", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("+150 XP")).toBeInTheDocument();
  });

  it("calls onComplete with quest id when circle button clicked", () => {
    const onComplete = vi.fn();
    render(
      <QuestCard quest={baseQuest} onComplete={onComplete} isCompleting={false} />
    );
    const button = screen.getByRole("button", { name: /complete quest/i });
    fireEvent.click(button);
    expect(onComplete).toHaveBeenCalledWith("quest-1");
  });

  it("does not call onComplete when quest is already completed", () => {
    const onComplete = vi.fn();
    const completedQuest = { ...baseQuest, is_completed: true };
    render(
      <QuestCard quest={completedQuest} onComplete={onComplete} isCompleting={false} />
    );
    const button = screen.getByRole("button", { name: /quest completed/i });
    fireEvent.click(button);
    expect(onComplete).not.toHaveBeenCalled();
  });

  it("shows domain badge", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("FITNESS")).toBeInTheDocument();
  });

  it("shows difficulty badge", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("shows estimated duration when present", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("30 min")).toBeInTheDocument();
  });

  it("disables button when isCompleting is true", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={true} />
    );
    const button = screen.getByRole("button", { name: /complete quest/i });
    expect(button).toBeDisabled();
  });

  it("shows completed styling when quest is done", () => {
    const completedQuest = { ...baseQuest, is_completed: true };
    const { container } = render(
      <QuestCard quest={completedQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("opacity-50");
  });

  it("shows context tags", () => {
    render(
      <QuestCard quest={baseQuest} onComplete={vi.fn()} isCompleting={false} />
    );
    expect(screen.getByText("#running")).toBeInTheDocument();
    expect(screen.getByText("#cardio")).toBeInTheDocument();
  });
});
