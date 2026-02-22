import json
import re
from typing import List
from app.schemas.quest import QuestCreate
from app.models.quest import QuestDomain, QuestDifficulty


def parse_quest_list(raw: str) -> List[QuestCreate]:
    clean = re.sub(r"```(json)?", "", raw).strip()

    json_start = min(
        (clean.find("{") if "{" in clean else 9999),
        (clean.find("[") if "[" in clean else 9999),
    )
    if json_start == 9999:
        raise ValueError(f"No JSON in agent output. Raw: {raw[:200]}")

    data = json.loads(clean[json_start:])
    quests_raw = data if isinstance(data, list) else data.get("quests", [])

    return [
        QuestCreate(
            title=q["title"],
            description=q["description"],
            domain=QuestDomain(q["domain"].lower()),
            difficulty=QuestDifficulty(q["difficulty"].lower()),
            xp_reward=int(q.get("xp_reward", 100)),
            stat_rewards=q.get("stat_rewards", {}),
            estimated_duration=q.get("estimated_duration", "30 min"),
            context_tags=q.get("context_tags", []),
            ai_generated=True,
        )
        for q in quests_raw
    ]
