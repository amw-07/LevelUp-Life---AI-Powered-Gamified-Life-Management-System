import random
from typing import Any
from crewai.tools import tool
from app.utils.game_mechanics import get_rank_from_xp, get_level_from_xp, get_rank_progress, calculate_streak
from app.utils.quote_db import select_quote


@tool("xp_calculator")
def calculate_xp_and_stats(domain: str, difficulty: str) -> dict[str, Any]:
    """Calculate XP reward and stat increases for completing a quest.
    Args: domain (fitness/productivity/learning), difficulty (easy/medium/hard).
    Returns dict with xp_reward and stat_rewards."""
    xp_ranges = {"easy": (40, 60), "medium": (80, 120), "hard": (160, 240)}
    stat_mapping = {
        "fitness": ["strength", "vitality", "endurance"],
        "productivity": ["focus", "efficiency", "execution"],
        "learning": ["intelligence", "creativity", "wisdom"],
    }
    lo, hi = xp_ranges.get(difficulty, (80, 120))
    xp_reward = random.randint(lo, hi)
    stats = stat_mapping.get(domain, [])
    stat_points = {"easy": 2, "medium": 5, "hard": 10}.get(difficulty, 2)
    stat_rewards = {}
    for i, stat in enumerate(stats):
        stat_rewards[stat] = stat_points if i == 0 else max(1, stat_points // 2)
    return {"xp_reward": xp_reward, "stat_rewards": stat_rewards}


@tool("rank_calculator")
def calculate_rank_and_level(total_xp: int) -> dict[str, Any]:
    """Calculate user rank and level based on total XP.
    Args: total_xp (int). Returns dict with rank, level, and progress info."""
    rank = get_rank_from_xp(total_xp)
    level = get_level_from_xp(total_xp)
    progress = get_rank_progress(total_xp)
    return {"rank": rank, "level": level, **progress}


@tool("difficulty_adjuster")
def adjust_quest_difficulty(level: int, completion_rate: float) -> dict[str, Any]:
    """Determine appropriate quest difficulty distribution based on user level and performance.
    Args: level (int), completion_rate (float 0-1). Returns dict with difficulty distribution."""
    if level <= 4:
        dist = {"easy": 0.7, "medium": 0.3, "hard": 0.0}
    elif level <= 14:
        dist = {"easy": 0.3, "medium": 0.5, "hard": 0.2}
    else:
        dist = {"easy": 0.1, "medium": 0.4, "hard": 0.5}
    if completion_rate < 0.5:
        dist = {
            "easy": min(1.0, dist["easy"] + 0.3),
            "medium": max(0.0, dist["medium"] - 0.2),
            "hard": max(0.0, dist["hard"] - 0.1),
        }
    return dist


@tool("quote_selector")
def select_motivational_quote(domain: str) -> dict[str, str]:
    """Select a contextually appropriate motivational quote for the given domain.
    Args: domain (fitness/productivity/learning/general). Returns dict with text and author."""
    return select_quote(domain)


@tool("streak_tracker")
def track_and_update_streak(last_active_iso: str, current_streak: int, longest_streak: int) -> dict[str, Any]:
    """Track user streaks and determine if streak continues or breaks.
    Args: last_active_iso (ISO datetime string), current_streak (int), longest_streak (int).
    Returns dict with updated streak information."""
    from datetime import datetime, timezone
    last_active = datetime.fromisoformat(last_active_iso).replace(tzinfo=timezone.utc)
    return calculate_streak(last_active, current_streak, longest_streak)


@tool("quest_generator_helper")
def generate_quest_ideas(domain: str, level: int, goals: list) -> list[dict[str, str]]:
    """Generate quest ideas based on domain, level, and user goals.
    Args: domain (str), level (int), goals (list of strings).
    Returns list of quest idea dicts with title and duration."""
    templates = {
        "fitness": {
            "easy": [
                {"title": "10-Minute Morning Stretch", "duration": "10 min"},
                {"title": "15-Minute Walk", "duration": "15 min"},
            ],
            "medium": [
                {"title": "30-Minute Workout Session", "duration": "30 min"},
                {"title": "45-Minute Cardio Activity", "duration": "45 min"},
            ],
            "hard": [
                {"title": "High-Intensity Interval Training", "duration": "45 min"},
                {"title": "Advanced Strength Training", "duration": "60 min"},
            ],
        },
        "productivity": {
            "easy": [
                {"title": "Plan Tomorrow's Top 3 Tasks", "duration": "10 min"},
                {"title": "25-Minute Focused Work Session", "duration": "25 min"},
            ],
            "medium": [
                {"title": "Complete Important Project Task", "duration": "90 min"},
                {"title": "Review and Optimize Workflow", "duration": "45 min"},
            ],
            "hard": [
                {"title": "Ship Major Project Milestone", "duration": "240 min"},
                {"title": "Full Day Deep Work Block", "duration": "360 min"},
            ],
        },
        "learning": {
            "easy": [
                {"title": "Read 10 Pages of Educational Book", "duration": "20 min"},
                {"title": "Watch Educational Video", "duration": "15 min"},
            ],
            "medium": [
                {"title": "Complete Online Course Module", "duration": "60 min"},
                {"title": "Practice Skill for 1 Hour", "duration": "60 min"},
            ],
            "hard": [
                {"title": "Build Project Using New Skill", "duration": "240 min"},
                {"title": "Master Complex Concept", "duration": "150 min"},
            ],
        },
    }
    if level <= 4:
        difficulty = "easy"
    elif level <= 14:
        difficulty = "medium"
    else:
        difficulty = "hard"
    pool = templates.get(domain, {}).get(difficulty, [])
    return random.sample(pool, min(2, len(pool)))


@tool("achievement_checker")
def check_achievements(quest_count: int, streak: int, xp: int) -> list[str]:
    """Check which achievements a user qualifies for based on their stats.
    Args: quest_count (int), streak (int), xp (int).
    Returns list of achievement keys earned."""
    from app.services.achievement_service import ACHIEVEMENT_DEFINITIONS
    return [
        defn["key"]
        for defn in ACHIEVEMENT_DEFINITIONS
        if defn["fn"](quest_count, streak, xp)
    ]
