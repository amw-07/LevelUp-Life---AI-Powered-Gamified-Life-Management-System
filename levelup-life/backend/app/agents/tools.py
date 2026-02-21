from app.utils.game_mechanics import get_rank_from_xp, get_level_from_xp, get_rank_progress, calculate_streak


def calculate_rank_and_level(xp: int) -> dict:
    return {
        "rank": get_rank_from_xp(xp),
        "level": get_level_from_xp(xp),
        "progress": get_rank_progress(xp),
    }


def track_and_update_streak(last_active_iso: str, current_streak: int, longest_streak: int) -> dict:
    from datetime import datetime, timezone
    last_active = datetime.fromisoformat(last_active_iso).replace(tzinfo=timezone.utc)
    return calculate_streak(last_active, current_streak, longest_streak)


def check_achievements(quest_count: int, streak: int, xp: int) -> list:
    from app.services.achievement_service import ACHIEVEMENT_DEFINITIONS
    return [
        defn["key"]
        for defn in ACHIEVEMENT_DEFINITIONS
        if defn["fn"](quest_count, streak, xp)
    ]


def adjust_quest_difficulty(level: int, completion_rate: float) -> dict:
    if level <= 4:
        dist = {"easy": 0.7, "medium": 0.3, "hard": 0.0}
    elif level <= 14:
        dist = {"easy": 0.3, "medium": 0.5, "hard": 0.2}
    else:
        dist = {"easy": 0.1, "medium": 0.4, "hard": 0.5}
    if completion_rate < 0.5:
        dist = {"easy": min(1.0, dist["easy"] + 0.3), "medium": max(0.0, dist["medium"] - 0.2), "hard": max(0.0, dist["hard"] - 0.1)}
    return dist


def generate_quest_ideas(domain: str, level: int, goals: list) -> list:
    return []


def calculate_xp_and_stats(difficulty: str, domain: str) -> dict:
    xp_ranges = {"easy": (40, 60), "medium": (80, 120), "hard": (160, 240)}
    import random
    lo, hi = xp_ranges.get(difficulty, (80, 120))
    return {"xp_reward": random.randint(lo, hi), "domain": domain}


def select_motivational_quote(domain: str) -> dict:
    from app.utils.quote_db import select_quote
    return select_quote(domain)
