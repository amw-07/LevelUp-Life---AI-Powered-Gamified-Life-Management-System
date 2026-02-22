from datetime import datetime, timezone, timedelta

RANK_THRESHOLDS = {
    "E": 0,
    "D": 1000,
    "C": 5000,
    "B": 15000,
    "A": 35000,
    "S": 70000,
    "SS": 150000,
}

RANKS = ["E", "D", "C", "B", "A", "S", "SS"]


def get_rank_from_xp(xp: int) -> str:
    current = "E"
    for rank in RANKS:
        if xp >= RANK_THRESHOLDS[rank]:
            current = rank
    return current


def get_level_from_xp(xp: int) -> int:
    return max(1, xp // 500 + 1)


def get_rank_progress(xp: int) -> dict:
    current = get_rank_from_xp(xp)
    idx = RANKS.index(current)
    if idx == len(RANKS) - 1:
        return {"percent": 100, "xp_needed": 0, "next_rank": None}
    next_rank = RANKS[idx + 1]
    lower = RANK_THRESHOLDS[current]
    upper = RANK_THRESHOLDS[next_rank]
    percent = ((xp - lower) / (upper - lower)) * 100
    return {"percent": percent, "xp_needed": upper - xp, "next_rank": next_rank}


def calculate_streak(
    last_active: datetime | None,
    current_streak: int,
    longest_streak: int,
) -> dict:
    now = datetime.now(timezone.utc)
    if last_active is None:
        new_streak = 1
    else:
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=timezone.utc)
        last_date = last_active.date()
        today = now.date()
        delta = (today - last_date).days
        if delta == 0:
            new_streak = current_streak
        elif delta == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1

    new_longest = max(longest_streak, new_streak)
    if new_streak == 1 and current_streak > 0 and new_streak < current_streak:
        message = "Streak reset. Start fresh today! 💪"
    elif new_streak > current_streak:
        message = f"Streak extended to {new_streak} days! 🔥"
    else:
        message = f"Streak maintained at {new_streak} days! ✅"

    return {
        "current_streak": new_streak,
        "longest_streak": new_longest,
        "message": message,
    }
