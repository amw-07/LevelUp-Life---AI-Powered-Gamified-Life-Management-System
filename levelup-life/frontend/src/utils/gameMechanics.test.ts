import { describe, it, expect } from "vitest";
import {
  getRankFromXp,
  getLevelFromXp,
  getRankProgress,
  getLevelProgress,
  getXpForNextLevel,
  RANK_THRESHOLDS,
  RANKS,
} from "./gameMechanics";

describe("getRankFromXp", () => {
  it("returns E rank at 0 xp", () => {
    expect(getRankFromXp(0)).toBe("E");
  });

  it("returns D rank at 1000 xp", () => {
    expect(getRankFromXp(1000)).toBe("D");
  });

  it("returns SS rank at 150000 xp", () => {
    expect(getRankFromXp(150000)).toBe("SS");
  });

  it("returns correct rank just below threshold", () => {
    expect(getRankFromXp(999)).toBe("E");
    expect(getRankFromXp(4999)).toBe("D");
  });

  it("returns correct rank at each threshold boundary", () => {
    expect(getRankFromXp(5000)).toBe("C");
    expect(getRankFromXp(15000)).toBe("B");
    expect(getRankFromXp(35000)).toBe("A");
    expect(getRankFromXp(70000)).toBe("S");
  });
});

describe("getLevelFromXp", () => {
  it("returns level 1 at 0 xp", () => {
    expect(getLevelFromXp(0)).toBe(1);
  });

  it("returns level 2 at 500 xp", () => {
    expect(getLevelFromXp(500)).toBe(2);
  });

  it("returns level 1 at 499 xp (minimum level 1)", () => {
    expect(getLevelFromXp(499)).toBe(1);
  });

  it("returns correct level for various xp values", () => {
    expect(getLevelFromXp(1000)).toBe(3);
    expect(getLevelFromXp(1500)).toBe(4);
    expect(getLevelFromXp(2499)).toBe(5);
  });
});

describe("getRankProgress", () => {
  it("returns 0% at rank E start", () => {
    const result = getRankProgress(0);
    expect(result.percent).toBe(0);
    expect(result.nextRank).toBe("D");
  });

  it("returns 100% at SS rank (max rank)", () => {
    const result = getRankProgress(150000);
    expect(result.percent).toBe(100);
    expect(result.nextRank).toBeNull();
    expect(result.xpNeeded).toBe(0);
  });

  it("calculates correct percent midway between ranks", () => {
    const lower = RANK_THRESHOLDS["E"];
    const upper = RANK_THRESHOLDS["D"];
    const midXp = lower + (upper - lower) / 2;
    const result = getRankProgress(midXp);
    expect(result.percent).toBeCloseTo(50, 1);
    expect(result.nextRank).toBe("D");
  });

  it("returns correct xpNeeded value", () => {
    const result = getRankProgress(500);
    expect(result.xpNeeded).toBe(RANK_THRESHOLDS["D"] - 500);
  });
});

describe("getLevelProgress", () => {
  it("returns 0 at start of a level", () => {
    expect(getLevelProgress(0)).toBe(0);
    expect(getLevelProgress(500)).toBe(0);
  });

  it("returns 50 at midpoint of a level", () => {
    expect(getLevelProgress(250)).toBe(50);
  });

  it("returns a number between 0 and 100", () => {
    const progress = getLevelProgress(750);
    expect(progress).toBeGreaterThanOrEqual(0);
    expect(progress).toBeLessThanOrEqual(100);
  });
});

describe("getXpForNextLevel", () => {
  it("returns 500 for level 1 (0 xp)", () => {
    expect(getXpForNextLevel(0)).toBe(500);
  });

  it("returns correct xp boundary for current level", () => {
    expect(getXpForNextLevel(500)).toBe(1000);
    expect(getXpForNextLevel(1000)).toBe(1500);
  });
});
